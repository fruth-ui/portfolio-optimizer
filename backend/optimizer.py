import numpy as np
import pandas as pd
import yfinance as yf
from joblib import Memory
from scipy.optimize import minimize
from typing import List, Tuple

memory = Memory(location=".cache", verbose=0)


@memory.cache
def fetch_prices(tickers: Tuple[str, ...], start_date: str, end_date: str) -> pd.DataFrame:
    data = yf.download(
        list(tickers),
        start=start_date,
        end=end_date,
        auto_adjust=True,
        progress=False,
    )
    if isinstance(data.columns, pd.MultiIndex):
        prices = data["Close"]
    else:
        prices = data[["Close"]] if "Close" in data.columns else data
        prices.columns = list(tickers)
    prices = prices.dropna(how="all").ffill().bfill()
    return prices


def compute_stats(prices: pd.DataFrame) -> Tuple[np.ndarray, np.ndarray]:
    log_returns = np.log(prices / prices.shift(1)).dropna()
    mu = log_returns.mean().values * 252
    cov = log_returns.cov().values * 252
    return mu, cov


def portfolio_performance(weights: np.ndarray, mu: np.ndarray, cov: np.ndarray, rf: float):
    ret = float(weights @ mu)
    vol = float(np.sqrt(weights @ cov @ weights))
    sharpe = (ret - rf) / vol if vol > 0 else 0.0
    return ret, vol, sharpe


def run_monte_carlo(
    mu: np.ndarray,
    cov: np.ndarray,
    rf: float,
    n: int,
    rng: np.random.Generator,
) -> np.ndarray:
    n_assets = len(mu)
    raw = rng.random((n, n_assets))
    weights = raw / raw.sum(axis=1, keepdims=True)

    returns = weights @ mu
    vols = np.sqrt(np.einsum("ij,jk,ik->i", weights, cov, weights))
    sharpes = (returns - rf) / np.where(vols > 0, vols, np.nan)

    results = np.column_stack([returns, vols, sharpes, weights])
    return results


def max_sharpe_portfolio(mu: np.ndarray, cov: np.ndarray, rf: float) -> np.ndarray:
    n = len(mu)

    def neg_sharpe(w):
        ret = w @ mu
        vol = np.sqrt(w @ cov @ w)
        return -(ret - rf) / vol if vol > 0 else 0.0

    constraints = [{"type": "eq", "fun": lambda w: w.sum() - 1}]
    bounds = [(0.0, 1.0)] * n
    best_result = None
    best_val = np.inf

    for _ in range(10):
        x0 = np.random.dirichlet(np.ones(n))
        res = minimize(neg_sharpe, x0, method="SLSQP", bounds=bounds, constraints=constraints)
        if res.success and res.fun < best_val:
            best_val = res.fun
            best_result = res.x

    return best_result if best_result is not None else np.ones(n) / n


def min_variance_portfolio(mu: np.ndarray, cov: np.ndarray) -> np.ndarray:
    n = len(mu)

    def portfolio_vol(w):
        return np.sqrt(w @ cov @ w)

    constraints = [{"type": "eq", "fun": lambda w: w.sum() - 1}]
    bounds = [(0.0, 1.0)] * n
    best_result = None
    best_val = np.inf

    for _ in range(10):
        x0 = np.random.dirichlet(np.ones(n))
        res = minimize(portfolio_vol, x0, method="SLSQP", bounds=bounds, constraints=constraints)
        if res.success and res.fun < best_val:
            best_val = res.fun
            best_result = res.x

    return best_result if best_result is not None else np.ones(n) / n


def optimize(
    tickers: List[str],
    start_date: str,
    end_date: str,
    rf_rate: float,
    n_simulations: int,
    n_plot_points: int = 800,
) -> dict:
    ticker_tuple = tuple(sorted(tickers))
    prices = fetch_prices(ticker_tuple, start_date, end_date)

    # Reorder columns to match user-specified order
    available = [t for t in tickers if t in prices.columns]
    prices = prices[available]

    if prices.empty or len(prices) < 2:
        raise ValueError(
            f"No price data returned for tickers {tickers}. "
            "Check ticker symbols, date range, and network connectivity."
        )

    tickers_ordered = list(prices.columns)
    mu, cov = compute_stats(prices)

    rng = np.random.default_rng(42)
    mc_results = run_monte_carlo(mu, cov, rf_rate, n_simulations, rng)

    # Columns: [return, vol, sharpe, w0, w1, ...]
    sample_idx = rng.choice(len(mc_results), size=min(n_plot_points, len(mc_results)), replace=False)
    sample = mc_results[sample_idx]

    portfolios = [
        {
            "return": float(row[0]),
            "vol": float(row[1]),
            "sharpe": float(row[2]),
            "weights": row[3:].tolist(),
        }
        for row in sample
    ]

    opt_w = max_sharpe_portfolio(mu, cov, rf_rate)
    opt_ret, opt_vol, opt_sharpe = portfolio_performance(opt_w, mu, cov, rf_rate)

    mv_w = min_variance_portfolio(mu, cov)
    mv_ret, mv_vol, mv_sharpe = portfolio_performance(mv_w, mu, cov, rf_rate)

    return {
        "tickers": tickers_ordered,
        "mu": mu.tolist(),
        "cov": cov.tolist(),
        "portfolios": portfolios,
        "optimal": {
            "weights": opt_w.tolist(),
            "return": opt_ret,
            "vol": opt_vol,
            "sharpe": opt_sharpe,
        },
        "minvar": {
            "weights": mv_w.tolist(),
            "return": mv_ret,
            "vol": mv_vol,
            "sharpe": mv_sharpe,
        },
    }

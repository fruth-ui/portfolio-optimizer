import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import plotly.figure_factory as ff
import pandas as pd
import numpy as np

from optimizer import optimize

st.set_page_config(
    page_title="Portfolio Optimizer",
    page_icon="📈",
    layout="wide",
)

st.title("📈 Portfolio Optimizer")
st.caption("Mean-variance optimization · Monte Carlo simulation · SciPy exact solver")

# ── Ticker presets ────────────────────────────────────────────────────────────
PRESETS = {
    "US Equities": ["AAPL", "MSFT", "GOOGL", "AMZN", "NVDA"],
    "Multi-Asset 60/40": ["SPY", "QQQ", "VTI", "AGG", "BND"],
    "Fixed Income": ["TLT", "IEF", "SHY", "LQD", "HYG", "AGG", "EMB"],
    "Equity + Bonds": ["AAPL", "MSFT", "AMZN", "TLT", "AGG", "LQD"],
    "Global Macro": ["SPY", "EEM", "GLD", "TLT", "DX-Y.NYB", "USO"],
}

POPULAR_TICKERS = [
    # US Large Cap Equities
    "AAPL", "MSFT", "GOOGL", "AMZN", "NVDA", "META", "TSLA", "BRK-B",
    "JPM", "V", "UNH", "XOM", "LLY", "JNJ", "WMT", "MA", "PG", "HD",
    "MRK", "ORCL", "ABBV", "BAC", "KO", "CVX", "PEP", "COST", "ADBE",
    "CSCO", "TMO", "MCD", "CRM", "ACN", "ABT", "NFLX", "AMD", "INTC",
    "QCOM", "TXN", "NEE", "PM", "GS", "BLK", "SPGI", "AXP", "INTU",
    # Broad Market ETFs
    "SPY", "QQQ", "VTI", "IVV", "VOO", "EEM", "VEA", "GLD", "SLV", "USO",
    # Fixed Income ETFs
    "AGG", "BND", "TLT", "IEF", "SHY", "LQD", "HYG", "EMB",
    "BNDX", "MUB", "VCIT", "VGIT", "VCSH", "BSV", "BIV", "IGLB",
    "FALN", "ANGL", "JNK", "SHYG", "FLOT", "NEAR",
]

# ── Sidebar controls ──────────────────────────────────────────────────────────
with st.sidebar:
    st.header("Settings")

    st.markdown("**Quick presets**")
    cols = st.columns(2)
    for i, (label, tkrs) in enumerate(PRESETS.items()):
        if cols[i % 2].button(label, use_container_width=True, key=f"preset_{label}"):
            st.session_state.selected_tickers = tkrs
            st.session_state.custom_tickers = []

    st.divider()

    if "custom_tickers" not in st.session_state:
        st.session_state.custom_tickers = []
    if "selected_tickers" not in st.session_state:
        st.session_state.selected_tickers = ["AAPL", "MSFT", "GOOGL", "AMZN", "NVDA"]

    all_options = POPULAR_TICKERS + [
        t for t in st.session_state.custom_tickers if t not in POPULAR_TICKERS
    ]

    selected = st.multiselect(
        "Select tickers",
        options=all_options,
        default=[t for t in st.session_state.selected_tickers if t in all_options],
        help="Type to search. Use presets above or add a custom symbol below.",
    )

    custom_input = st.text_input(
        "Add custom ticker",
        placeholder="e.g. TSM, ASML, 9988.HK",
    )
    if custom_input:
        ct = custom_input.strip().upper()
        if ct and ct not in st.session_state.custom_tickers:
            st.session_state.custom_tickers.append(ct)
            st.rerun()

    tickers = selected + [t for t in st.session_state.custom_tickers if t not in selected]

    if st.session_state.custom_tickers:
        st.caption(f"Custom: {', '.join(st.session_state.custom_tickers)}")
        if st.button("Clear custom tickers", use_container_width=True):
            st.session_state.custom_tickers = []
            st.rerun()

    st.divider()

    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input("Start date", value=pd.Timestamp("2020-01-01"))
    with col2:
        end_date = st.date_input("End date", value=pd.Timestamp("2024-12-31"))

    rf_rate = st.number_input(
        "Risk-free rate",
        min_value=0.0, max_value=1.0, value=0.05, step=0.01, format="%.2f",
        help="Annual risk-free rate as a decimal (e.g. 0.05 = 5%)",
    )
    n_simulations = st.slider("Simulations", 500, 20000, 5000, 500)

    run = st.button("Optimize", type="primary", use_container_width=True)

# ── Run optimization ──────────────────────────────────────────────────────────
if run:
    if len(tickers) < 2:
        st.error("Please select at least 2 tickers.")
        st.stop()
    with st.spinner("Fetching prices and running simulation…"):
        try:
            result = optimize(
                tickers=tickers,
                start_date=str(start_date),
                end_date=str(end_date),
                rf_rate=rf_rate,
                n_simulations=n_simulations,
                n_plot_points=800,
            )
            st.session_state["result"] = result
        except Exception as e:
            st.error(f"Optimization failed: {e}")
            st.stop()

if "result" not in st.session_state:
    st.info("Configure settings in the sidebar and click **Optimize**.")
    st.stop()

result = st.session_state["result"]
portfolios = result["portfolios"]
optimal = result["optimal"]
minvar = result["minvar"]
tickers_out = result["tickers"]

# ── Efficient frontier ────────────────────────────────────────────────────────
st.subheader("Efficient Frontier")

df = pd.DataFrame({
    "Volatility": [p["vol"] * 100 for p in portfolios],
    "Return": [p["return"] * 100 for p in portfolios],
    "Sharpe": [p["sharpe"] for p in portfolios],
})
df = df[np.isfinite(df["Sharpe"])]

fig = go.Figure()
fig.add_trace(go.Scatter(
    x=df["Volatility"], y=df["Return"], mode="markers",
    marker=dict(size=5, color=df["Sharpe"], colorscale="RdYlGn",
                showscale=True, colorbar=dict(title="Sharpe"), opacity=0.65),
    hovertemplate="Vol: %{x:.2f}%<br>Return: %{y:.2f}%<br>Sharpe: %{marker.color:.3f}<extra></extra>",
    name="Simulated portfolios",
))
fig.add_trace(go.Scatter(
    x=[optimal["vol"] * 100], y=[optimal["return"] * 100], mode="markers",
    marker=dict(size=18, symbol="star", color="#facc15", line=dict(color="#b45309", width=2)),
    name=f"Max Sharpe ({optimal['sharpe']:.3f})",
    hovertemplate=f"Max Sharpe<br>Return: {optimal['return']*100:.2f}%<br>Vol: {optimal['vol']*100:.2f}%<extra></extra>",
))
fig.add_trace(go.Scatter(
    x=[minvar["vol"] * 100], y=[minvar["return"] * 100], mode="markers",
    marker=dict(size=18, symbol="diamond", color="#ec4899", line=dict(color="#9d174d", width=2)),
    name=f"Min Variance ({minvar['sharpe']:.3f})",
    hovertemplate=f"Min Variance<br>Return: {minvar['return']*100:.2f}%<br>Vol: {minvar['vol']*100:.2f}%<extra></extra>",
))
fig.update_layout(
    xaxis_title="Volatility (%)", yaxis_title="Expected Return (%)",
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    height=420, margin=dict(l=40, r=20, t=20, b=40),
)
st.plotly_chart(fig, use_container_width=True)

# ── Backtest ──────────────────────────────────────────────────────────────────
st.subheader("Backtested Cumulative Return ($1 invested)")

bt = result["backtest"]
bt_df = pd.DataFrame({
    "Date": pd.to_datetime(bt["dates"]),
    "Max Sharpe": bt["optimal"],
    "Min Variance": bt["minvar"],
    "Equal Weight": bt["equal_weight"],
})

fig_bt = go.Figure()
for col, color in [("Max Sharpe", "#facc15"), ("Min Variance", "#ec4899"), ("Equal Weight", "#94a3b8")]:
    fig_bt.add_trace(go.Scatter(
        x=bt_df["Date"], y=bt_df[col], mode="lines", name=col,
        line=dict(color=color, width=2 if col != "Equal Weight" else 1.5,
                  dash="dot" if col == "Equal Weight" else "solid"),
        hovertemplate=f"{col}: $%{{y:.3f}}<extra></extra>",
    ))
fig_bt.update_layout(
    xaxis_title="", yaxis_title="Portfolio Value ($)",
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    height=320, margin=dict(l=40, r=20, t=20, b=30),
    hovermode="x unified",
)
st.plotly_chart(fig_bt, use_container_width=True)

# ── Metrics + weights ─────────────────────────────────────────────────────────
tab1, tab2 = st.tabs(["⭐ Max Sharpe Portfolio", "🔵 Min Variance Portfolio"])


def show_portfolio(p, tickers_out, label):
    m1, m2, m3 = st.columns(3)
    m1.metric("Expected Return (ann.)", f"{p['return']*100:.2f}%")
    m2.metric("Volatility (ann.)", f"{p['vol']*100:.2f}%")
    m3.metric("Sharpe Ratio", f"{p['sharpe']:.3f}")

    m4, m5, m6 = st.columns(3)
    m4.metric("Sortino Ratio", f"{p['sortino']:.3f}",
              help="Return per unit of downside deviation")
    m5.metric("Max Drawdown", f"{p['max_drawdown']*100:.2f}%",
              help="Worst peak-to-trough decline in sample period")
    m6.metric("Daily VaR (95%)", f"{p['var_95']*100:.2f}%",
              help="Historical 1-day loss not exceeded 95% of trading days")

    st.markdown(f"**{label} Weights**")
    weights_df = (
        pd.DataFrame({"Ticker": tickers_out, "Weight": [w * 100 for w in p["weights"]]})
        .sort_values("Weight", ascending=True)
    )
    fig_bar = px.bar(
        weights_df, x="Weight", y="Ticker", orientation="h",
        text=weights_df["Weight"].map(lambda v: f"{v:.1f}%"),
        color="Weight", color_continuous_scale="Blues", range_x=[0, 100],
    )
    fig_bar.update_traces(textposition="outside")
    fig_bar.update_layout(
        coloraxis_showscale=False,
        height=max(200, len(tickers_out) * 50),
        margin=dict(l=20, r=60, t=10, b=20),
        xaxis_title="Weight (%)", yaxis_title="",
    )
    st.plotly_chart(fig_bar, use_container_width=True)


with tab1:
    show_portfolio(optimal, tickers_out, "Max Sharpe")

with tab2:
    show_portfolio(minvar, tickers_out, "Min Variance")

# ── Correlation heatmap ───────────────────────────────────────────────────────
st.subheader("Asset Correlation Matrix")
st.caption("Pairwise correlation of daily log returns over the selected period")

corr = np.array(result["corr"])
fig_corr = go.Figure(go.Heatmap(
    z=corr,
    x=tickers_out,
    y=tickers_out,
    colorscale="RdBu_r",
    zmid=0,
    zmin=-1, zmax=1,
    text=np.round(corr, 2),
    texttemplate="%{text}",
    textfont=dict(size=11),
    hoverongaps=False,
    colorbar=dict(title="ρ"),
))
fig_corr.update_layout(
    height=max(350, len(tickers_out) * 55),
    margin=dict(l=20, r=20, t=10, b=20),
    xaxis=dict(tickangle=-45),
)
st.plotly_chart(fig_corr, use_container_width=True)

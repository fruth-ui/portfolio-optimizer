import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np

from optimizer import optimize

st.set_page_config(
    page_title="Portfolio Optimizer",
    page_icon="📈",
    layout="wide",
)

st.title("📈 Portfolio Optimizer")
st.caption("Mean-variance optimization via Monte Carlo + SciPy")

# ── Sidebar controls ──────────────────────────────────────────────────────────
with st.sidebar:
    st.header("Settings")

    POPULAR_TICKERS = [
        "AAPL", "MSFT", "GOOGL", "AMZN", "NVDA", "META", "TSLA", "BRK-B",
        "JPM", "V", "UNH", "XOM", "LLY", "JNJ", "WMT", "MA", "PG", "HD",
        "MRK", "ORCL", "ABBV", "BAC", "KO", "CVX", "PEP", "COST", "ADBE",
        "CSCO", "TMO", "MCD", "CRM", "ACN", "ABT", "NFLX", "AMD", "INTC",
        "QCOM", "TXN", "NEE", "PM", "RTX", "HON", "AMGN", "IBM", "GE",
        "CAT", "GS", "BLK", "SPGI", "AXP", "INTU", "BKNG", "ISRG", "SYK",
        "T", "VZ", "DIS", "PYPL", "UBER", "LYFT", "SNAP", "SPOT", "SQ",
        "COIN", "PLTR", "ARM", "SMCI", "MU", "LRCX", "AMAT", "KLAC",
    ]

    # Keep any custom tickers the user added in previous runs
    if "custom_tickers" not in st.session_state:
        st.session_state.custom_tickers = []

    all_options = POPULAR_TICKERS + [
        t for t in st.session_state.custom_tickers if t not in POPULAR_TICKERS
    ]

    selected = st.multiselect(
        "Select tickers",
        options=all_options,
        default=["AAPL", "MSFT", "GOOGL", "AMZN", "NVDA"],
        help="Search and select from the list below",
    )

    custom_input = st.text_input(
        "Add a custom ticker",
        placeholder="e.g. TSM, ASML, 9988.HK",
        help="Type any ticker not in the list above, then press Enter",
    )
    if custom_input:
        custom_ticker = custom_input.strip().upper()
        if custom_ticker and custom_ticker not in st.session_state.custom_tickers:
            st.session_state.custom_tickers.append(custom_ticker)
            st.rerun()

    tickers = selected + [
        t for t in st.session_state.custom_tickers if t not in selected
    ]
    if st.session_state.custom_tickers:
        st.caption(f"Custom: {', '.join(st.session_state.custom_tickers)}")
        if st.button("Clear custom tickers", use_container_width=True):
            st.session_state.custom_tickers = []
            st.rerun()

    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input("Start date", value=pd.Timestamp("2020-01-01"))
    with col2:
        end_date = st.date_input("End date", value=pd.Timestamp("2024-12-31"))

    rf_rate = st.number_input(
        "Risk-free rate", min_value=0.0, max_value=1.0,
        value=0.05, step=0.01, format="%.2f",
        help="Annual risk-free rate as a decimal (e.g. 0.05 = 5%)",
    )
    n_simulations = st.slider(
        "Simulations", min_value=500, max_value=20000,
        value=5000, step=500,
    )

    run = st.button("Optimize", type="primary", use_container_width=True)

# ── Run optimization ──────────────────────────────────────────────────────────
if run:
    if len(tickers) < 2:
        st.error("Please enter at least 2 tickers.")
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
        except Exception as e:
            st.error(f"Optimization failed: {e}")
            st.stop()

    st.session_state["result"] = result

if "result" not in st.session_state:
    st.info("Configure settings in the sidebar and click **Optimize**.")
    st.stop()

result = st.session_state["result"]
portfolios = result["portfolios"]
optimal = result["optimal"]
minvar = result["minvar"]
tickers_out = result["tickers"]

# ── Efficient frontier scatter ────────────────────────────────────────────────
st.subheader("Efficient Frontier")

df = pd.DataFrame({
    "Volatility": [p["vol"] * 100 for p in portfolios],
    "Return": [p["return"] * 100 for p in portfolios],
    "Sharpe": [p["sharpe"] for p in portfolios],
})
df = df[np.isfinite(df["Sharpe"])]

fig = go.Figure()

fig.add_trace(go.Scatter(
    x=df["Volatility"],
    y=df["Return"],
    mode="markers",
    marker=dict(
        size=5,
        color=df["Sharpe"],
        colorscale="RdYlGn",
        showscale=True,
        colorbar=dict(title="Sharpe"),
        opacity=0.7,
    ),
    hovertemplate="Vol: %{x:.2f}%<br>Return: %{y:.2f}%<br>Sharpe: %{marker.color:.3f}<extra></extra>",
    name="Simulated portfolios",
))

fig.add_trace(go.Scatter(
    x=[optimal["vol"] * 100],
    y=[optimal["return"] * 100],
    mode="markers",
    marker=dict(size=18, symbol="star", color="#facc15", line=dict(color="#b45309", width=2)),
    name=f"Max Sharpe ({optimal['sharpe']:.3f})",
    hovertemplate=f"Max Sharpe<br>Return: {optimal['return']*100:.2f}%<br>Vol: {optimal['vol']*100:.2f}%<extra></extra>",
))

fig.add_trace(go.Scatter(
    x=[minvar["vol"] * 100],
    y=[minvar["return"] * 100],
    mode="markers",
    marker=dict(size=18, symbol="diamond", color="#ec4899", line=dict(color="#9d174d", width=2)),
    name=f"Min Variance ({minvar['sharpe']:.3f})",
    hovertemplate=f"Min Variance<br>Return: {minvar['return']*100:.2f}%<br>Vol: {minvar['vol']*100:.2f}%<extra></extra>",
))

fig.update_layout(
    xaxis_title="Volatility (%)",
    yaxis_title="Expected Return (%)",
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    height=450,
    margin=dict(l=40, r=20, t=20, b=40),
)

st.plotly_chart(fig, use_container_width=True)

# ── Metrics + weights ─────────────────────────────────────────────────────────
tab1, tab2 = st.tabs(["⭐ Max Sharpe Portfolio", "🔵 Min Variance Portfolio"])

def show_portfolio(p, tickers_out, label):
    c1, c2, c3 = st.columns(3)
    c1.metric("Expected Return", f"{p['return']*100:.2f}%")
    c2.metric("Volatility", f"{p['vol']*100:.2f}%")
    c3.metric("Sharpe Ratio", f"{p['sharpe']:.3f}")

    st.markdown(f"**{label} Weights**")
    weights_df = (
        pd.DataFrame({"Ticker": tickers_out, "Weight": [w * 100 for w in p["weights"]]})
        .sort_values("Weight", ascending=True)
    )
    fig_bar = px.bar(
        weights_df,
        x="Weight",
        y="Ticker",
        orientation="h",
        text=weights_df["Weight"].map(lambda v: f"{v:.1f}%"),
        color="Weight",
        color_continuous_scale="Blues",
        range_x=[0, 100],
    )
    fig_bar.update_traces(textposition="outside")
    fig_bar.update_layout(
        coloraxis_showscale=False,
        height=max(200, len(tickers_out) * 50),
        margin=dict(l=20, r=60, t=10, b=20),
        xaxis_title="Weight (%)",
        yaxis_title="",
    )
    st.plotly_chart(fig_bar, use_container_width=True)

with tab1:
    show_portfolio(optimal, tickers_out, "Max Sharpe")

with tab2:
    show_portfolio(minvar, tickers_out, "Min Variance")

# Portfolio Optimizer

Mean-variance portfolio optimization using Monte Carlo simulation and SciPy exact optimization. Built with FastAPI (Python) + React + Recharts + Tailwind.

## Features

- Fetch historical adjusted closing prices via **yfinance** (disk-cached with joblib)
- **Monte Carlo simulation** of random long-only portfolios (configurable, default 5 000)
- **Exact optimization** via `scipy.optimize.minimize` for the max-Sharpe and min-variance portfolios
- **Efficient frontier** scatter plot colored by Sharpe ratio
- Horizontal bar chart of portfolio weights; metrics panel showing return, volatility, Sharpe

---

## Setup

### Prerequisites

- Python 3.11+
- Node.js 18+

---

### Backend

```bash
cd portfolio-optimizer/backend

# Create and activate a virtual environment
python3 -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Start the dev server (port 8000)
uvicorn main:app --reload
```

The API will be available at `http://localhost:8000`.  
Interactive docs: `http://localhost:8000/docs`

---

### Frontend

```bash
cd portfolio-optimizer/frontend

# Install dependencies
npm install

# Start the Vite dev server (port 5173, proxies /optimize → localhost:8000)
npm run dev
```

Open `http://localhost:5173` in your browser.

---

## API

### `POST /optimize`

**Request body:**
```json
{
  "tickers":       ["AAPL", "MSFT", "GOOGL", "AMZN", "NVDA"],
  "start_date":    "2020-01-01",
  "end_date":      "2024-12-31",
  "rf_rate":       0.05,
  "n_simulations": 5000
}
```

**Response:**
```json
{
  "tickers":    ["AAPL", "MSFT", "GOOGL", "AMZN", "NVDA"],
  "mu":         [...],
  "cov":        [[...]],
  "portfolios": [{"return": 0.18, "vol": 0.14, "sharpe": 0.93, "weights": [...]}],
  "optimal":    {"weights": [...], "return": 0.21, "vol": 0.15, "sharpe": 1.07},
  "minvar":     {"weights": [...], "return": 0.16, "vol": 0.12, "sharpe": 0.92}
}
```

---

## Project Structure

```
portfolio-optimizer/
  backend/
    main.py           # FastAPI app + CORS middleware
    optimizer.py      # yfinance fetch, joblib cache, MC simulation, scipy optimization
    requirements.txt
  frontend/
    src/
      App.jsx
      components/
        TickerInput.jsx    # Add/remove chip UI
        FrontierChart.jsx  # Recharts scatter plot
        WeightsChart.jsx   # Horizontal bar chart
        MetricsPanel.jsx   # Return / Vol / Sharpe cards
    package.json
    vite.config.js         # Proxy /optimize → :8000
  .gitignore               # Excludes .cache/, node_modules/, dist/
  README.md
```

---

## Notes

- yfinance results are cached in `.cache/` (excluded from git). Delete this folder to force a fresh fetch.
- The scatter plot shows up to 800 randomly sampled points from the full simulation for performance; optimization always uses all simulated data.
- Risk-free rate is entered as a decimal (e.g., `0.05` = 5%).

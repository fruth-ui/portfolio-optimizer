import { useState } from "react";
import TickerInput from "./components/TickerInput";
import FrontierChart from "./components/FrontierChart";
import WeightsChart from "./components/WeightsChart";
import MetricsPanel from "./components/MetricsPanel";

const DEFAULT_TICKERS = ["AAPL", "MSFT", "GOOGL", "AMZN", "NVDA"];
const DEFAULT_START = "2020-01-01";
const DEFAULT_END = "2024-12-31";

function Spinner() {
  return (
    <div className="flex flex-col items-center justify-center py-24 gap-4">
      <div className="w-12 h-12 border-4 border-indigo-200 border-t-indigo-600 rounded-full animate-spin" />
      <p className="text-gray-500 text-sm">Running Monte Carlo simulation…</p>
    </div>
  );
}

function ErrorBanner({ message }) {
  return (
    <div className="mt-4 p-4 bg-red-50 border border-red-200 rounded-lg text-red-700 text-sm">
      <strong>Error:</strong> {message}
    </div>
  );
}

export default function App() {
  const [tickers, setTickers] = useState(DEFAULT_TICKERS);
  const [startDate, setStartDate] = useState(DEFAULT_START);
  const [endDate, setEndDate] = useState(DEFAULT_END);
  const [rfRate, setRfRate] = useState(0.05);
  const [nSims, setNSims] = useState(5000);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [result, setResult] = useState(null);
  const [activeTab, setActiveTab] = useState("optimal");

  async function handleOptimize() {
    if (tickers.length < 2) {
      setError("Please add at least 2 tickers.");
      return;
    }
    setLoading(true);
    setError(null);
    setResult(null);
    try {
      const resp = await fetch("/optimize", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          tickers,
          start_date: startDate,
          end_date: endDate,
          rf_rate: rfRate,
          n_simulations: nSims,
        }),
      });
      if (!resp.ok) {
        const body = await resp.json().catch(() => ({}));
        throw new Error(body.detail || `HTTP ${resp.status}`);
      }
      const data = await resp.json();
      setResult(data);
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white border-b border-gray-200 px-6 py-4">
        <h1 className="text-xl font-bold text-indigo-700 tracking-tight">
          Portfolio Optimizer
        </h1>
        <p className="text-xs text-gray-500 mt-0.5">
          Mean-variance optimization via Monte Carlo + SciPy
        </p>
      </header>

      <main className="max-w-7xl mx-auto px-4 py-6 space-y-6">
        {/* Controls panel */}
        <div className="bg-white rounded-xl border border-gray-200 shadow-sm p-5">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
            <div className="md:col-span-2">
              <TickerInput tickers={tickers} onChange={setTickers} />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Start Date</label>
              <input
                type="date"
                value={startDate}
                onChange={(e) => setStartDate(e.target.value)}
                className="w-full border border-gray-300 rounded-md px-3 py-1.5 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-400"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">End Date</label>
              <input
                type="date"
                value={endDate}
                onChange={(e) => setEndDate(e.target.value)}
                className="w-full border border-gray-300 rounded-md px-3 py-1.5 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-400"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Risk-Free Rate
              </label>
              <div className="relative">
                <input
                  type="number"
                  value={rfRate}
                  onChange={(e) => setRfRate(parseFloat(e.target.value))}
                  step="0.01"
                  min="0"
                  max="1"
                  className="w-full border border-gray-300 rounded-md px-3 py-1.5 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-400"
                />
                <span className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 text-sm pointer-events-none">
                  {(rfRate * 100).toFixed(1)}%
                </span>
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Simulations
              </label>
              <input
                type="number"
                value={nSims}
                onChange={(e) => setNSims(parseInt(e.target.value, 10))}
                step="500"
                min="100"
                max="50000"
                className="w-full border border-gray-300 rounded-md px-3 py-1.5 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-400"
              />
            </div>
          </div>

          <div className="mt-5 flex justify-end">
            <button
              onClick={handleOptimize}
              disabled={loading}
              className="px-6 py-2 bg-indigo-600 text-white font-semibold rounded-lg hover:bg-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              {loading ? "Optimizing…" : "Optimize"}
            </button>
          </div>
        </div>

        {error && <ErrorBanner message={error} />}
        {loading && <Spinner />}

        {result && !loading && (
          <>
            {/* Efficient frontier */}
            <div className="bg-white rounded-xl border border-gray-200 shadow-sm p-5">
              <FrontierChart
                portfolios={result.portfolios}
                optimal={result.optimal}
                minvar={result.minvar}
              />
            </div>

            {/* Tabs: Optimal vs MinVar */}
            <div className="bg-white rounded-xl border border-gray-200 shadow-sm p-5">
              <div className="flex gap-3 mb-5 border-b border-gray-200">
                {[
                  { id: "optimal", label: "Max Sharpe Portfolio" },
                  { id: "minvar", label: "Min Variance Portfolio" },
                ].map((tab) => (
                  <button
                    key={tab.id}
                    onClick={() => setActiveTab(tab.id)}
                    className={`pb-2 px-1 text-sm font-medium border-b-2 transition-colors ${
                      activeTab === tab.id
                        ? "border-indigo-600 text-indigo-700"
                        : "border-transparent text-gray-500 hover:text-gray-700"
                    }`}
                  >
                    {tab.label}
                  </button>
                ))}
              </div>

              <div className="space-y-6">
                <MetricsPanel
                  optimal={result.optimal}
                  minvar={result.minvar}
                  label={activeTab === "optimal" ? "Max Sharpe Portfolio" : "Min Variance Portfolio"}
                />
                <WeightsChart
                  tickers={result.tickers}
                  weights={
                    activeTab === "optimal"
                      ? result.optimal.weights
                      : result.minvar.weights
                  }
                  title={
                    activeTab === "optimal"
                      ? "Max Sharpe Weights"
                      : "Min Variance Weights"
                  }
                />
              </div>
            </div>
          </>
        )}
      </main>
    </div>
  );
}

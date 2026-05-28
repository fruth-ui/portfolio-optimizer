function pct(v) {
  return (v * 100).toFixed(2) + "%";
}

function Metric({ label, value }) {
  return (
    <div className="bg-white rounded-lg border border-gray-200 p-4 flex flex-col items-center">
      <span className="text-xs font-medium text-gray-500 uppercase tracking-wide">{label}</span>
      <span className="mt-1 text-2xl font-bold text-indigo-700">{value}</span>
    </div>
  );
}

export default function MetricsPanel({ optimal, minvar, label = "Max Sharpe Portfolio" }) {
  const p = label === "Max Sharpe Portfolio" ? optimal : minvar;
  return (
    <div>
      <h3 className="text-sm font-semibold text-gray-600 mb-3">{label}</h3>
      <div className="grid grid-cols-3 gap-3">
        <Metric label="Expected Return" value={pct(p.return)} />
        <Metric label="Volatility" value={pct(p.vol)} />
        <Metric label="Sharpe Ratio" value={p.sharpe.toFixed(3)} />
      </div>
    </div>
  );
}

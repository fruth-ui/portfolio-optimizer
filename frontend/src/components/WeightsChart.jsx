import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  Cell,
  LabelList,
} from "recharts";

const COLORS = [
  "#6366f1", "#8b5cf6", "#ec4899", "#f59e0b",
  "#10b981", "#3b82f6", "#ef4444", "#14b8a6",
];

export default function WeightsChart({ tickers, weights, title = "Portfolio Weights" }) {
  const data = tickers
    .map((t, i) => ({ ticker: t, weight: parseFloat((weights[i] * 100).toFixed(2)) }))
    .sort((a, b) => b.weight - a.weight);

  return (
    <div>
      <h3 className="text-sm font-semibold text-gray-600 mb-2">{title}</h3>
      <ResponsiveContainer width="100%" height={Math.max(180, data.length * 42)}>
        <BarChart
          data={data}
          layout="vertical"
          margin={{ top: 4, right: 60, bottom: 4, left: 48 }}
        >
          <XAxis
            type="number"
            domain={[0, 100]}
            tickFormatter={(v) => `${v}%`}
            tick={{ fontSize: 11 }}
          />
          <YAxis
            dataKey="ticker"
            type="category"
            tick={{ fontSize: 12, fontWeight: 600 }}
            width={42}
          />
          <Tooltip formatter={(v) => `${v.toFixed(2)}%`} />
          <Bar dataKey="weight" radius={[0, 4, 4, 0]} isAnimationActive={false}>
            {data.map((entry, i) => (
              <Cell key={i} fill={COLORS[i % COLORS.length]} />
            ))}
            <LabelList
              dataKey="weight"
              position="right"
              formatter={(v) => `${v.toFixed(1)}%`}
              style={{ fontSize: 11, fill: "#374151" }}
            />
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}

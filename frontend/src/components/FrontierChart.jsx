import {
  ScatterChart,
  Scatter,
  XAxis,
  YAxis,
  ZAxis,
  Tooltip,
  ResponsiveContainer,
  Cell,
} from "recharts";

function sharpeColor(sharpe, min, max) {
  const t = Math.max(0, Math.min(1, (sharpe - min) / (max - min + 1e-9)));
  // Blue → Green → Yellow → Red (low → high)
  const r = Math.round(t < 0.5 ? 30 + t * 2 * 200 : 230);
  const g = Math.round(t < 0.5 ? 100 + t * 2 * 130 : 230 - (t - 0.5) * 2 * 180);
  const b = Math.round(t < 0.5 ? 200 - t * 2 * 170 : 30);
  return `rgb(${r},${g},${b})`;
}

function CustomTooltip({ active, payload }) {
  if (!active || !payload?.length) return null;
  const d = payload[0].payload;
  return (
    <div className="bg-white border border-gray-200 rounded-lg shadow-md p-3 text-xs space-y-1">
      <p>Return: <strong>{(d.return * 100).toFixed(2)}%</strong></p>
      <p>Vol: <strong>{(d.vol * 100).toFixed(2)}%</strong></p>
      <p>Sharpe: <strong>{d.sharpe.toFixed(3)}</strong></p>
    </div>
  );
}

export default function FrontierChart({ portfolios, optimal, minvar }) {
  const sharpes = portfolios.map((p) => p.sharpe).filter(Number.isFinite);
  const minS = Math.min(...sharpes);
  const maxS = Math.max(...sharpes);

  const optPoint = [{ vol: optimal.vol, return: optimal.return, sharpe: optimal.sharpe }];
  const mvPoint = [{ vol: minvar.vol, return: minvar.return, sharpe: minvar.sharpe }];

  return (
    <div>
      <h3 className="text-sm font-semibold text-gray-600 mb-2">Efficient Frontier</h3>
      <div className="flex items-center gap-6 mb-3 text-xs text-gray-500">
        <span className="flex items-center gap-1">
          <span className="inline-block w-3 h-3 rounded-full bg-yellow-400 border-2 border-yellow-600" />
          Max Sharpe
        </span>
        <span className="flex items-center gap-1">
          <span className="inline-block w-3 h-3 rounded-full bg-pink-500 border-2 border-pink-700" />
          Min Variance
        </span>
        <span className="ml-auto flex items-center gap-1">
          <span className="text-blue-400 font-bold">Low</span>
          <span
            className="inline-block h-2 w-24 rounded"
            style={{
              background: "linear-gradient(to right, rgb(30,100,200), rgb(230,230,30), rgb(230,50,30))",
            }}
          />
          <span className="text-red-400 font-bold">High</span>
          <span className="ml-1">Sharpe</span>
        </span>
      </div>
      <ResponsiveContainer width="100%" height={360}>
        <ScatterChart margin={{ top: 10, right: 20, bottom: 20, left: 20 }}>
          <XAxis
            dataKey="vol"
            type="number"
            name="Volatility"
            domain={["auto", "auto"]}
            tickFormatter={(v) => `${(v * 100).toFixed(0)}%`}
            label={{ value: "Volatility", position: "insideBottom", offset: -10, fontSize: 12 }}
          />
          <YAxis
            dataKey="return"
            type="number"
            name="Return"
            domain={["auto", "auto"]}
            tickFormatter={(v) => `${(v * 100).toFixed(0)}%`}
            label={{ value: "Expected Return", angle: -90, position: "insideLeft", offset: 10, fontSize: 12 }}
          />
          <ZAxis range={[18, 18]} />
          <Tooltip content={<CustomTooltip />} />

          {/* MC scatter */}
          <Scatter data={portfolios} isAnimationActive={false}>
            {portfolios.map((p, i) => (
              <Cell
                key={i}
                fill={Number.isFinite(p.sharpe) ? sharpeColor(p.sharpe, minS, maxS) : "#ccc"}
                fillOpacity={0.7}
              />
            ))}
          </Scatter>

          {/* Max Sharpe */}
          <Scatter
            data={optPoint}
            shape="star"
            isAnimationActive={false}
            legendType="none"
          >
            <Cell fill="#facc15" stroke="#b45309" strokeWidth={2} />
          </Scatter>

          {/* Min Variance */}
          <Scatter
            data={mvPoint}
            shape="diamond"
            isAnimationActive={false}
            legendType="none"
          >
            <Cell fill="#ec4899" stroke="#9d174d" strokeWidth={2} />
          </Scatter>
        </ScatterChart>
      </ResponsiveContainer>
    </div>
  );
}

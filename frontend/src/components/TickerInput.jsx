import { useState } from "react";

export default function TickerInput({ tickers, onChange }) {
  const [input, setInput] = useState("");

  function addTicker() {
    const t = input.trim().toUpperCase();
    if (t && !tickers.includes(t)) {
      onChange([...tickers, t]);
    }
    setInput("");
  }

  function removeTicker(t) {
    onChange(tickers.filter((x) => x !== t));
  }

  function handleKeyDown(e) {
    if (e.key === "Enter" || e.key === ",") {
      e.preventDefault();
      addTicker();
    }
  }

  return (
    <div>
      <label className="block text-sm font-medium text-gray-700 mb-1">Tickers</label>
      <div className="flex flex-wrap gap-2 mb-2 min-h-[2.25rem]">
        {tickers.map((t) => (
          <span
            key={t}
            className="inline-flex items-center gap-1 bg-indigo-100 text-indigo-800 text-sm font-medium px-2.5 py-0.5 rounded-full"
          >
            {t}
            <button
              type="button"
              onClick={() => removeTicker(t)}
              className="text-indigo-500 hover:text-indigo-800 leading-none"
              aria-label={`Remove ${t}`}
            >
              ×
            </button>
          </span>
        ))}
      </div>
      <div className="flex gap-2">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value.toUpperCase())}
          onKeyDown={handleKeyDown}
          placeholder="Add ticker (Enter or comma)"
          className="flex-1 border border-gray-300 rounded-md px-3 py-1.5 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-400"
        />
        <button
          type="button"
          onClick={addTicker}
          className="px-3 py-1.5 bg-indigo-600 text-white text-sm rounded-md hover:bg-indigo-700"
        >
          Add
        </button>
      </div>
    </div>
  );
}

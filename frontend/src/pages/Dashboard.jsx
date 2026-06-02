import { useEffect, useState } from "react";
import {
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

export default function Dashboard() {
  const [selectedCard, setSelectedCard] = useState(null);
  const [series, setSeries] = useState([]);

  const specId = 2306882;

  useEffect(() => {
    fetch(`http://localhost:8000/card/${specId}`)
      .then((r) => r.json())
      .then((data) => {
        setSelectedCard(data.spec_id);

        // normalize for chart (NOW includes latest)
        const cleaned = (data.timeseries || []).map((p) => ({
          date: p.date,
          avg: typeof p.avg === "number" ? p.avg : null,
          latest: typeof p.latest === "number" ? p.latest : null,
          qty: p.qty ?? 0,
        }));

        setSeries(cleaned);
      });
  }, []);

  return (
    <div style={{ padding: 20 }}>
      <h1>🔥 PSA Momentum Dashboard</h1>

      <h3>Spec ID: {selectedCard}</h3>

      {/* 📊 CHART */}
      <div style={{ width: "100%", height: 300, marginBottom: 30 }}>
        <ResponsiveContainer>
          <LineChart data={series}>
            <XAxis dataKey="date" />
            <YAxis />
            <Tooltip />

            {/* 📈 Avg price (baseline trend) */}
            <Line
              type="monotone"
              dataKey="avg"
              stroke="#4f46e5"
              strokeWidth={2}
              dot={false}
            />

            {/* 🚀 Latest price (hype / spikes / sentiment) */}
            <Line
              type="monotone"
              dataKey="latest"
              stroke="#ef4444"
              strokeWidth={2}
              dot={false}
            />
          </LineChart>
        </ResponsiveContainer>
      </div>

      {/* 📋 TABLE */}
      <table border="1" cellPadding="10">
        <thead>
          <tr>
            <th>Date</th>
            <th>Avg Price</th>
            <th>Latest Price</th>
            <th>Qty</th>
          </tr>
        </thead>

        <tbody>
          {series.map((p) => (
            <tr key={p.date}>
              <td>{p.date}</td>

              <td>€{typeof p.avg === "number" ? p.avg.toFixed(2) : "—"}</td>

              <td>
                €{typeof p.latest === "number" ? p.latest.toFixed(2) : "—"}
              </td>

              <td>{p.qty ?? "—"}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

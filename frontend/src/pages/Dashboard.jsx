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
        console.log(data.timeseries[0]);

        setSelectedCard(data.spec_id);

        const cleaned = (data.timeseries || []).map((p) => ({
          date: p.date,
          avg: typeof p.avg === "number" ? p.avg : null,
          latest: typeof p.latest === "number" ? p.latest : null,
          qty: p.qty ?? 0,
          momentum: typeof p.momentum === "number" ? p.momentum : null,
        }));

        setSeries(cleaned);
      });
  }, []);

  // ✅ safe last point (always aligned correctly)
  const lastPoint = series.length > 0 ? series[series.length - 1] : null;

  return (
    <div style={{ padding: 20 }}>
      <h1>🔥 PSA Momentum Dashboard</h1>

      <h3>Spec ID: {selectedCard}</h3>

      {/* 📊 CHART */}
      <div style={{ width: "100%", height: 300, marginBottom: 30 }}>
        <ResponsiveContainer>
          <LineChart data={series}>
            {/* X axis */}
            <XAxis dataKey="date" />

            {/* Price axis */}
            <YAxis yAxisId="price" />

            {/* Momentum axis */}
            <YAxis yAxisId="momentum" orientation="right" />

            <Tooltip />

            {/* 🔵 Avg price (trend) */}
            <Line
              yAxisId="price"
              type="monotone"
              dataKey="avg"
              stroke="#4f46e5"
              strokeWidth={2}
              dot={false}
            />

            {/* 🟢 Momentum (signal) */}
            <Line
              yAxisId="momentum"
              type="monotone"
              dataKey="momentum"
              stroke="#10b981"
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
            <th>Momentum</th>
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

              <td>{p.momentum?.toFixed(3) ?? "—"}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

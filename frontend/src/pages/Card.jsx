import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import {
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

export default function Card() {
  const { id } = useParams();
  const [series, setSeries] = useState([]);
  const [specId, setSpecId] = useState(null);

  useEffect(() => {
    fetch(`http://localhost:8000/card/${id}`)
      .then((r) => r.json())
      .then((d) => {
        setSpecId(d.spec_id);

        const cleaned = (d.timeseries || []).map((p) => ({
          date: p.date,
          avg: typeof p.avg === "number" ? p.avg : null,
          latest: typeof p.latest === "number" ? p.latest : null,
          momentum: typeof p.momentum === "number" ? p.momentum : null,
          qty: p.qty ?? 0,
        }));

        setSeries(cleaned);
      });
  }, [id]);

  return (
    <div style={{ padding: 20 }}>
      <h1>📈 Card Detail View</h1>
      <h3>Spec ID: {specId}</h3>

      <div style={{ width: "100%", height: 400 }}>
        <ResponsiveContainer>
          <LineChart data={series}>
            <XAxis dataKey="date" />

            {/* price axis */}
            <YAxis yAxisId="price" />

            {/* momentum axis */}
            <YAxis yAxisId="momentum" orientation="right" />

            <Tooltip />

            {/* Avg price (trend) */}
            <Line
              yAxisId="price"
              type="monotone"
              dataKey="avg"
              stroke="#4f46e5"
              strokeWidth={2}
              dot={false}
            />

            {/* Latest price (actual sales pressure) */}
            <Line
              yAxisId="price"
              type="monotone"
              dataKey="latest"
              stroke="#ef4444"
              strokeWidth={2}
              dot={false}
            />

            {/* Momentum signal */}
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

      {/* Optional debug table */}
      <table border="1" cellPadding="8" style={{ marginTop: 20 }}>
        <thead>
          <tr>
            <th>Date</th>
            <th>Avg</th>
            <th>Latest</th>
            <th>Qty</th>
            <th>Momentum</th>
          </tr>
        </thead>

        <tbody>
          {series.map((p) => (
            <tr key={p.date}>
              <td>{p.date}</td>
              <td>{p.avg ?? "—"}</td>
              <td>{p.latest ?? "—"}</td>
              <td>{p.qty}</td>
              <td>{p.momentum?.toFixed(3) ?? "—"}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

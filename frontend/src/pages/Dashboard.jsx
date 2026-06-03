import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import {
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

export default function Dashboard() {
  const [cards, setCards] = useState([]);
  const navigate = useNavigate();

  useEffect(() => {
    // Fetch card snapshots first
    fetch("http://localhost:8000/cards")
      .then((r) => r.json())
      .then(async (snapshotCards) => {
        // For each card, fetch its full timeseries
        const cardsWithSeries = await Promise.all(
          snapshotCards.map(async (card) => {
            try {
              const resp = await fetch(
                `http://localhost:8000/card/${card.spec_id}`,
              );
              const data = await resp.json();
              // Map timeseries to cleaned series
              const series = (data.timeseries || []).map((p) => ({
                date: p.date,
                avg: p.avg ?? null,
                momentum: p.momentum ?? null,
              }));
              return { ...card, series };
            } catch (err) {
              console.error("Error fetching timeseries for", card.spec_id, err);
              return { ...card, series: [] };
            }
          }),
        );

        setCards(cardsWithSeries);
      });
  }, []);

  return (
    <div style={{ padding: 20 }}>
      <h1>🔥 PSA Momentum Dashboard</h1>

      {/* Grid of cards */}
      <div style={{ display: "grid", gap: 20 }}>
        {cards.map((card) => (
          <div
            key={card.spec_id}
            style={{
              border: "1px solid #ccc",
              borderRadius: 8,
              padding: 12,
              cursor: "pointer",
              transition: "box-shadow 0.2s",
            }}
            onClick={() => navigate(`/card/${card.spec_id}`)}
            onMouseEnter={(e) => {
              e.currentTarget.style.boxShadow = "0 0 10px rgba(0,0,0,0.3)";
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.boxShadow = "none";
            }}
          >
            <h3>{card.name}</h3>
            <p>Spec ID: {card.spec_id}</p>
            <p>Avg: €{card.avg?.toFixed(2)}</p>
            <p>Latest: €{card.latest?.toFixed(2)}</p>
            <p>Momentum: {card.momentum?.toFixed(3)}</p>

            {/* Mini sparkline chart */}
            <div style={{ width: "100%", height: 150, marginTop: 10 }}>
              <ResponsiveContainer>
                <LineChart data={card.series}>
                  <XAxis dataKey="date" hide />
                  <YAxis yAxisId="price" hide domain={["dataMin", "dataMax"]} />
                  <YAxis
                    yAxisId="momentum"
                    orientation="right"
                    hide
                    domain={["dataMin", "dataMax"]}
                  />
                  <Tooltip />
                  <Line
                    yAxisId="price"
                    type="monotone"
                    dataKey="avg"
                    stroke="#4f46e5"
                    strokeWidth={2}
                    dot={false}
                  />
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
          </div>
        ))}
      </div>
    </div>
  );
}

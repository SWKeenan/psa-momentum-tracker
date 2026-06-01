import { useEffect, useState } from "react";

export default function Dashboard() {
  const [cards, setCards] = useState([]);

  useEffect(() => {
    fetch("http://localhost:8000/cards")
      .then((r) => r.json())
      .then(setCards);
  }, []);

  return (
    <div style={{ padding: 20 }}>
      <h1>🔥 PSA Momentum Dashboard</h1>

      <table border="1" cellPadding="10">
        <thead>
          <tr>
            <th>Card</th>
            <th>Avg Price</th>
          </tr>
        </thead>

        <tbody>
          {cards.map((c) => (
            <tr key={c.spec_id}>
              <td>{c.name}</td>
              <td>€{c.avg.toFixed(2)}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

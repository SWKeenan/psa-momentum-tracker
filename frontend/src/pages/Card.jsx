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
  const [data, setData] = useState([]);

  useEffect(() => {
    fetch(`http://localhost:8000/card/${id}`)
      .then((r) => r.json())
      .then((d) => {
        setData(
          d.sales.map((s) => ({
            date: s[0],
            price: s[1],
          })),
        );
      });
  }, [id]);

  return (
    <div style={{ padding: 20 }}>
      <h1>Card Price History</h1>

      <div style={{ width: "100%", height: 400 }}>
        <ResponsiveContainer>
          <LineChart data={data}>
            <XAxis dataKey="date" />
            <YAxis />
            <Tooltip />
            <Line type="monotone" dataKey="price" stroke="black" />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}

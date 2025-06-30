import { useEffect, useState } from "react";
import { LineChart, Line, CartesianGrid, XAxis, YAxis, Tooltip, Legend, ResponsiveContainer } from "recharts";

export default function TvlChart({ protocol }) {
  const [data, setData] = useState([]);

  useEffect(() => {
    fetch(`http://localhost:8000/tvl/${protocol.toLowerCase()}`)
      .then((res) => res.json())
      .then((json) => {
        // Expecting array of { timestamp, tvl }
        setData(json);
      })
      .catch((err) => console.error(err));
  }, [protocol]);

  return (
    <div className="bg-white p-4 rounded shadow">
      <h2 className="text-xl font-semibold mb-2">{protocol} TVL Over Time</h2>
      <ResponsiveContainer width="100%" height={300}>
        <LineChart data={data}>
          <CartesianGrid stroke="#eee" />
          <XAxis dataKey="timestamp" />
          <YAxis />
          <Tooltip />
          <Legend />
          <Line type="monotone" dataKey="tvl" stroke="#3b82f6" />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}

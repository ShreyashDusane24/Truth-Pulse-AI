import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip } from "recharts";

const data = [
  { day: "Jan 15", claims: 45 },
  { day: "Jan 16", claims: 52 },
  { day: "Jan 17", claims: 38 },
  { day: "Jan 18", claims: 67 },
  { day: "Jan 19", claims: 58 },
  { day: "Jan 20", claims: 74 },
  { day: "Jan 21", claims: 81 },
];

export default function LineChartCard() {
  return (
    <div className="bg-white p-6 rounded-2xl shadow-md border">
      <h3 className="text-lg font-semibold mb-4">False Claims Over Time</h3>
      <LineChart width={380} height={240} data={data}>
        <CartesianGrid strokeDasharray="3 3" />
        <XAxis dataKey="day" />
        <YAxis />
        <Tooltip />
        <Line type="monotone" dataKey="claims" stroke="#2563EB" strokeWidth={3} />
      </LineChart>
    </div>
  );
}

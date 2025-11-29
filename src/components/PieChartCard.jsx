import { PieChart, Pie, Cell, Legend } from "recharts";

const data = [
  { name: "Health", value: 35 },
  { name: "Politics", value: 30 },
  { name: "Finance", value: 20 },
  { name: "Technology", value: 15 },
];

const COLORS = ["#2563EB", "#10B981", "#F59E0B", "#14B8A6"];

export default function PieChartCard() {
  return (
    <div className="bg-white p-6 rounded-2xl shadow-md border">
      <h3 className="text-lg font-semibold mb-4">Category Breakdown</h3>
      <PieChart width={380} height={260}>
        <Pie
          data={data}
          dataKey="value"
          cx="50%"
          cy="50%"
          outerRadius={95}
          label
        >
          {data.map((_, i) => (
            <Cell key={i} fill={COLORS[i]} />
          ))}
        </Pie>
        <Legend />
      </PieChart>
    </div>
  );
}

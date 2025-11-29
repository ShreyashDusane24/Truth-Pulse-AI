import { PieChart, Pie, Cell } from "recharts";

export default function ScoreGauge({ score }) {
  const data = [
    { value: score },
    { value: 100 - score },
  ];

  const COLORS = ["#10B981", "#E5E7EB"];

  return (
    <div className="flex flex-col items-center">
      <PieChart width={200} height={200}>
        <Pie
          data={data}
          cx={100}
          cy={100}
          innerRadius={70}
          outerRadius={90}
          startAngle={180}
          endAngle={0}
          paddingAngle={3}
          dataKey="value"
        >
          {data.map((_, i) => (
            <Cell key={i} fill={COLORS[i]} />
          ))}
        </Pie>
      </PieChart>

      <p className="text-3xl font-bold -mt-16">{score}%</p>
      <p className="text-gray-500">Truth Score</p>
    </div>
  );
}

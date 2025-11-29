import LineChartCard from "../components/LineChartCard";
import PieChartCard from "../components/PieChartCard";
import AlertCard from "../components/AlertCard";

export default function Trends() {
  return (
    <div className="px-8 py-10">
      <AlertCard />

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mt-6">
        <LineChartCard />
        <PieChartCard />
      </div>
    </div>
  );
}

import { useState } from "react";
import ScoreGauge from "../components/ScoreGauge";

export default function Verify() {
  const [text, setText] = useState("");
  const [score, setScore] = useState(null);

  const analyze = () => {
    setScore(Math.floor(Math.random() * 100));
  };

  return (
    <div className="px-8 py-10 grid grid-cols-1 lg:grid-cols-2 gap-8">
      <div className="bg-white p-6 rounded-2xl shadow-md border">
        <h2 className="text-xl font-semibold mb-4">Enter Claim to Verify</h2>
        <textarea
          rows="6"
          value={text}
          onChange={(e) => setText(e.target.value)}
          className="w-full border rounded-xl p-3"
        />
        <button
          onClick={analyze}
          className="w-full mt-4 py-3 rounded-xl text-white bg-gradient-to-r from-blue-500 to-green-400"
        >
          Verify Claim
        </button>
      </div>

      {score !== null && (
        <div className="bg-white p-6 rounded-2xl shadow-md border">
          <ScoreGauge score={score} />
          <p
            className={`text-center font-semibold mt-3 ${
              score < 40
                ? "text-red-500"
                : score < 70
                ? "text-yellow-500"
                : "text-green-500"
            }`}
          >
            {score < 40
              ? "False Information"
              : score < 70
              ? "Partially True"
              : "Likely True"}
          </p>
        </div>
      )}
    </div>
  );
}

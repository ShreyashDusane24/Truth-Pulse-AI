import { Link } from "react-router-dom";

export default function Home() {
  return (
    <div className="pt-24 text-center px-6 max-w-4xl mx-auto">
      <h1 className="text-5xl font-bold text-gray-900 leading-tight">
        Detect Misinformation.
        <span className="text-brand"> Verify Truth.</span>
      </h1>

      <p className="text-gray-600 text-lg mt-4">
        TruthPulse AI verifies claims, detects misinformation, and provides
        evidence-based truth scores in seconds.
      </p>

      <div className="mt-10 bg-white shadow-md p-6 rounded-2xl max-w-2xl mx-auto border">
        <input
          placeholder="Paste any claim, headline or statement..."
          className="w-full p-3 rounded-xl border focus:outline-brand"
        />

        <Link
          to="/verify"
          className="block w-full mt-4 py-3 rounded-xl text-white font-medium bg-gradient-to-r from-blue-500 to-green-400"
        >
          Verify Now
        </Link>
      </div>
    </div>
  );
}

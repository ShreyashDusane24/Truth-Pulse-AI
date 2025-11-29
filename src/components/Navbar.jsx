import { Link, NavLink } from "react-router-dom";

export default function Navbar() {
  return (
    <nav className="w-full flex items-center justify-between px-8 py-4 bg-white shadow-sm sticky top-0 z-50">
      <Link to="/" className="flex items-center gap-2 text-xl font-semibold">
        <span className="text-brand">🛡 TruthPulse AI</span>
      </Link>

      <div className="flex gap-6 text-gray-700 font-medium">
        <NavLink to="/verify">Verify</NavLink>
        <NavLink to="/trends">Trends</NavLink>
        <NavLink to="/chat">Chat</NavLink>
        <NavLink to="/about">About</NavLink>
      </div>

      <Link
        to="/verify"
        className="px-4 py-2 rounded-full bg-gradient-to-r from-blue-500 to-green-400 text-white font-medium"
      >
        + Verify Claim
      </Link>
    </nav>
  );
}

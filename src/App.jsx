import { BrowserRouter, Routes, Route } from "react-router-dom";
import Navbar from "./components/Navbar";
import Home from "./pages/Home";
import Verify from "./pages/Verify";
import Trends from "./pages/Trends";
import About from "./pages/About";
import Chat from "./pages/Chat";

function App() {
  return (
    <BrowserRouter>
      <Navbar />
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/verify" element={<Verify />} />
        <Route path="/trends" element={<Trends />} />
        <Route path="/chat" element={<Chat />} />
        <Route path="/about" element={<About />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;

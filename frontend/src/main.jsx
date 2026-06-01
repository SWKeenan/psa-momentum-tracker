import ReactDOM from "react-dom/client";
import { BrowserRouter, Route, Routes } from "react-router-dom";
import Card from "./pages/Card";
import Dashboard from "./pages/Dashboard";

ReactDOM.createRoot(document.getElementById("root")).render(
  <BrowserRouter>
    <Routes>
      <Route path="/" element={<Dashboard />} />
      <Route path="/card/:id" element={<Card />} />
    </Routes>
  </BrowserRouter>,
);

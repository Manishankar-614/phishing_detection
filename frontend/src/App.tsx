import { useState } from "react";
import DetectionPage from "./pages/DetectionPage";
import AdminDashboard from "./pages/AdminDashboard";
import "./index.css";

function App() {
  const [currentView, setCurrentView] = useState<"scanner" | "admin">("admin");

  return (
    <>
      {currentView === "admin" ? (
        <AdminDashboard onNavigateScanner={() => setCurrentView("scanner")} />
      ) : (
        <DetectionPage onNavigateAdmin={() => setCurrentView("admin")} />
      )}
    </>
  );
}

export default App;
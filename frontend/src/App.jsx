import { useState, useEffect } from "react";
import ChatBox from "./components/ChatBox";
import AdminLogin from "./admin/AdminLogin";
import AdminDashboard from "./admin/AdminDashboard";
import "./index.css";

export default function App() {
  const [role, setRole] = useState("student");
  const [studentId, setStudentId] = useState("");
  const [darkMode, setDarkMode] = useState(false);

  const [isAdminMode, setIsAdminMode] = useState(false); // Chat vs Admin
  const [isAuthenticated, setIsAuthenticated] = useState(false); // Token valid

  // Handle Dark Mode
  useEffect(() => {
    if (darkMode) {
      document.body.classList.add("dark");
    } else {
      document.body.classList.remove("dark");
    }
  }, [darkMode]);

  // Logout Admin
  const logoutAdmin = () => {
    localStorage.removeItem("admin_token");
    setIsAuthenticated(false);
    setIsAdminMode(false);
  };

  return (
    <div className="app">
      <header>
        <h1>School Chatbot</h1>
      </header>

      {/* Top Controls */}
      <div className="controls">
        <button onClick={() => setIsAdminMode(false)}>
          Chat Mode
        </button>

        <button onClick={() => setIsAdminMode(true)}>
          Admin Mode
        </button>

        <button
          className="dark-toggle"
          onClick={() => setDarkMode(!darkMode)}
        >
          {darkMode ? "☀️" : "🌙"}
        </button>
      </div>

      {/* Main View */}
      {!isAdminMode ? (
        <ChatBox role={role} studentId={studentId} />
      ) : isAuthenticated ? (
        <AdminDashboard onLogout={logoutAdmin} />
      ) : (
        <AdminLogin onLogin={() => setIsAuthenticated(true)} />
      )}
    </div>
  );
}

import { useState, useEffect } from "react";
import ChatBox from "./components/ChatBox";
import "./index.css";

export default function App() {
  const [role, setRole] = useState("student");
  const [studentId, setStudentId] = useState("");
  const [darkMode, setDarkMode] = useState(false);

  // Apply dark mode to body
  useEffect(() => {
    if (darkMode) {
      document.body.classList.add("dark");
    } else {
      document.body.classList.remove("dark");
    }
  }, [darkMode]);

  // Load saved theme
  useEffect(() => {
    const saved = localStorage.getItem("darkMode");
    if (saved === "true") {
      setDarkMode(true);
    }
  }, []);

  return (
    <div className="app">
      <header>
        <h1>School Chatbot</h1>

        
      </header>

      <div className="controls">
        <label>
          Role:
          <select value={role} onChange={(e) => setRole(e.target.value)}>
            <option value="student">Student</option>
            <option value="parent">Parent</option>
          </select>
        </label>

        <label>
          Student ID:
          <input
            type="number"
            placeholder="Enter student ID"
            value={studentId}
            onChange={(e) => setStudentId(e.target.value)}
          />
        </label>
        <label>
          <button
          className="dark-toggle"
          onClick={() => setDarkMode(!darkMode)}
          title="Toggle dark mode"
        >
          {darkMode ? "☀️" : "🌙"}
        </button>
        </label>
      </div>

      <ChatBox role={role} studentId={studentId} />
    </div>
  );
}

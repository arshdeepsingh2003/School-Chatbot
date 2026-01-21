import { useState } from "react";
import ChatBox from "./components/ChatBox";
import "./index.css";

export default function App() {
  const [role, setRole] = useState("student");
  const [studentId, setStudentId] = useState("");

  return (
    <div className="app">
      <header>
        <h1>School Chatbot</h1>
        <button className="dark-toggle" onClick={() => document.body.classList.toggle("dark")}>🌙</button>

        
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
      </div>

      <ChatBox role={role} studentId={studentId} />
    </div>
  );
}

import { useState } from "react";
import AdminStudents from "./AdminStudents";

export default function AdminDashboard({ onLogout }) {
  const [tab, setTab] = useState("students");

  return (
    <div className="admin-panel">
      <h2>🎛️ Admin Dashboard</h2>

      <div style={{ display: "flex", gap: "10px" }}>
        <button onClick={() => setTab("students")}>
          Students
        </button>

        <button onClick={() => setTab("marks")}>
          Marks
        </button>

        <button onClick={() => setTab("report")}>
          Report
        </button>

        <button onClick={onLogout}>
          Logout
        </button>
      </div>

      <AdminStudents mode={tab} />
    </div>
  );
}

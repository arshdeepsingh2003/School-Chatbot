import { useState, useEffect, useRef } from "react";
import axios from "axios";
import AdminStudents from "./AdminStudents";

export default function AdminDashboard({ onLogout }) {
  const [tab, setTab] = useState("students");
  const checkedRef = useRef(false); // 🔥 prevent repeated checks

  useEffect(() => {
    if (checkedRef.current) return;
    checkedRef.current = true;

    const token = localStorage.getItem("admin_token");

    if (!token) {
      onLogout();
      return;
    }

    axios
      .get(`${import.meta.env.VITE_API_BASE_URL}/admin/check`, {
        headers: { "X-Admin-Token": token }
      })
      .catch(() => {
        localStorage.removeItem("admin_token");
        onLogout(); // silent logout — no message spam
      });
  }, []);

  return (
    <div className="admin-panel">
      <h2>🎛️ Admin Dashboard</h2>

      <div style={{ display: "flex", gap: "10px", marginBottom: "10px" }}>
        <button onClick={() => setTab("students")}>Students</button>
        <button onClick={() => setTab("marks")}>Marks</button>
        <button onClick={() => setTab("report")}>Report</button>
        <button onClick={onLogout}>Logout</button>
      </div>

      <AdminStudents mode={tab} />
    </div>
  );
}

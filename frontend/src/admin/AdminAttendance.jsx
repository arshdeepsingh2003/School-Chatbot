import { useState, useEffect } from "react";
import {
  getAttendanceSummary,
  getAttendanceMonth,
  exportAttendance
} from "../services/adminApi";

import { PieChart, Pie, Tooltip, ResponsiveContainer, Cell } from "recharts";
import "./admin.css";

export default function AdminAttendance() {
  const [studentId, setStudentId] = useState("");
  const [summary, setSummary] = useState(null);
  const [calendar, setCalendar] = useState([]);
  const [year, setYear] = useState(new Date().getFullYear());
  const [month, setMonth] = useState(new Date().getMonth() + 1);
  const [message, setMessage] = useState("");

  // 🎨 Pie colors: Present = Green, Absent = Red
  const COLORS = ["#22c55e", "#ef4444"];

  // 🔔 Auto-hide messages
  useEffect(() => {
    if (!message) return;
    const t = setTimeout(() => setMessage(""), 4000);
    return () => clearTimeout(t);
  }, [message]);

  // ---------------- LOAD SUMMARY ----------------
  const loadSummary = async () => {
    if (!studentId) {
      setMessage("❌ Enter student ID first");
      return;
    }

    try {
      const res = await getAttendanceSummary(studentId);
      setSummary(res.data);
      setMessage("📊 Summary loaded successfully");
    } catch (err) {
      setSummary(null);
      setMessage(
        "❌ " + (err.response?.data?.detail || "No attendance data found")
      );
    }
  };

  // ---------------- LOAD MONTH ----------------
  const loadMonth = async () => {
    if (!studentId) {
      setMessage("❌ Enter student ID first");
      return;
    }

    try {
      const res = await getAttendanceMonth(studentId, year, month);
      setCalendar(res.data);
      setMessage("📅 Monthly view loaded");
    } catch (err) {
      setCalendar([]);
      setMessage(
        "❌ " + (err.response?.data?.detail || "Failed to load month data")
      );
    }
  };

  // ---------------- EXPORT EXCEL ----------------
  const downloadExcel = async () => {
    if (!studentId) {
      setMessage("❌ Enter student ID first");
      return;
    }

    try {
      const res = await exportAttendance(studentId);

      const url = window.URL.createObjectURL(new Blob([res.data]));
      const link = document.createElement("a");

      link.href = url;
      link.setAttribute("download", `attendance_${studentId}.xlsx`);

      document.body.appendChild(link);
      link.click();
      link.remove();

      setMessage("📤 Excel downloaded successfully");
    } catch (err) {
      setMessage(
        "❌ " + (err.response?.data?.detail || "Export failed")
      );
    }
  };

  // ---------------- CHART DATA ----------------
  const chartData = summary
    ? [
        { name: "Present", value: summary.present },
        { name: "Absent", value: summary.absent }
      ]
    : [];

  return (
    <div className="admin-panel">
      {/* MESSAGE */}
      {message && (
        <div
          className={`admin-message ${
            message.startsWith("📊") ||
            message.startsWith("📅") ||
            message.startsWith("📤")
              ? "success"
              : "error"
          }`}
        >
          {message}
        </div>
      )}

      <h3>📊 Attendance Dashboard</h3>

      {/* STUDENT ID */}
      <input
        type="number"
        placeholder="Student ID"
        value={studentId}
        onChange={(e) => setStudentId(e.target.value)}
      />

      {/* ACTION BUTTONS */}
      <div
        style={{
          display: "flex",
          gap: "10px",
          margin: "10px 0"
        }}
      >
        <button onClick={loadSummary}>
          Load Summary
        </button>

        <button onClick={downloadExcel}>
          Export Excel
        </button>
      </div>

      {/* SUMMARY + CHART */}
      {summary && (
        <>
          <p>Total: {summary.total}</p>
          <p>Present: {summary.present}</p>
          <p>Absent: {summary.absent}</p>
          <p>Attendance %: {summary.percentage}%</p>

          <div
            style={{
              width: "100%",
              height: 250
            }}
          >
            <ResponsiveContainer>
              <PieChart>
                <Pie
                  data={chartData}
                  dataKey="value"
                  nameKey="name"
                  outerRadius={80}
                  label
                >
                  {chartData.map((entry, index) => (
                    <Cell
                      key={`cell-${index}`}
                      fill={COLORS[index % COLORS.length]}
                    />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </div>

          {/* LEGEND */}
          <div
            style={{
              display: "flex",
              justifyContent: "center",
              gap: "20px",
              marginTop: "5px"
            }}
          >
            <span style={{ color: COLORS[0] }}>● Present</span>
            <span style={{ color: COLORS[1] }}>● Absent</span>
          </div>
        </>
      )}

      <hr />

      {/* MONTHLY CALENDAR */}
      <h4>📅 Monthly Calendar</h4>

      <div
        style={{
          display: "flex",
          gap: "10px",
          marginBottom: "10px"
        }}
      >
        <input
          type="number"
          placeholder="Year"
          value={year}
          onChange={(e) => setYear(e.target.value)}
        />

        <input
          type="number"
          placeholder="Month (1-12)"
          value={month}
          onChange={(e) => setMonth(e.target.value)}
        />

        <button onClick={loadMonth}>
          Load Month
        </button>
      </div>

      {calendar.length > 0 ? (
        <ul>
          {calendar.map((d, i) => (
            <li key={i}>
              {d.date} — {d.status}
            </li>
          ))}
        </ul>
      ) : (
        <p style={{ opacity: 0.7 }}>
          No monthly attendance loaded yet
        </p>
      )}
    </div>
  );
}

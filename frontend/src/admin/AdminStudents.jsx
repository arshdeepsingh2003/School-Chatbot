import { useEffect, useState } from "react";
import {
  getStudents,
  addStudent,
  updateStudent,
  deleteStudent,
  addMarks,
  addAttendance,
  getReport
} from "../services/adminApi";

export default function AdminStudents({ mode }) {
  const [students, setStudents] = useState([]);
  const [form, setForm] = useState({ id: "", name: "" });
  const [marks, setMarks] = useState([{ subject: "", score: "" }]);
  const [attendance, setAttendance] = useState({
    date: "",
    status: "Present"
  });
  const [report, setReport] = useState(null);
  const [message, setMessage] = useState("");

  // -------- AUTO-HIDE MESSAGE --------
  useEffect(() => {
    if (!message) return;
    const t = setTimeout(() => setMessage(""), 4000);
    return () => clearTimeout(t);
  }, [message]);

  // -------- LOAD STUDENTS --------
  const loadStudents = async () => {
    try {
      const res = await getStudents();
      setStudents(res.data);
    } catch {
      setMessage("❌ Failed to load students");
    }
  };

  useEffect(() => {
    if (mode === "students") loadStudents();
  }, [mode]);

  // -------- STUDENT ACTIONS --------
  const handleAddStudent = async () => {
    try {
      const res = await addStudent(form.id, form.name);
      setMessage("✅ " + res.data.message);
      loadStudents();
    } catch (err) {
      setMessage("⚠️ " + (err.response?.data?.detail || "Failed to add student"));
    }
  };

  const handleUpdateStudent = async () => {
    try {
      const res = await updateStudent(form.id, form.name);
      setMessage("✅ " + res.data.message);
      loadStudents();
    } catch (err) {
      setMessage("❌ " + (err.response?.data?.detail || "Failed to update student"));
    }
  };

  const handleDeleteStudent = async () => {
    try {
      const res = await deleteStudent(form.id);
      setMessage("🗑️ " + res.data.message);
      loadStudents();
    } catch (err) {
      setMessage("❌ " + (err.response?.data?.detail || "Failed to delete student"));
    }
  };

  // -------- MULTI-MARKS --------
  const addMoreMarks = () => {
    setMarks([...marks, { subject: "", score: "" }]);
  };

  const updateMarks = (index, field, value) => {
    const copy = [...marks];
    copy[index][field] = value;
    setMarks(copy);
  };

  const handleSaveMarks = async () => {
    try {
      for (const m of marks) {
        if (m.subject && m.score) {
          const res = await addMarks(form.id, m.subject, m.score);
          setMessage("✅ " + res.data.message);
        }
      }
      setMarks([{ subject: "", score: "" }]);
    } catch (err) {
      setMessage("❌ " + (err.response?.data?.detail || "Failed to save marks"));
    }
  };

  // -------- ATTENDANCE --------
  const handleSaveAttendance = async () => {
    try {
      const res = await addAttendance(
        form.id,
        attendance.date,
        attendance.status
      );
      setMessage("✅ " + res.data.message);
    } catch (err) {
      setMessage("❌ " + (err.response?.data?.detail || "Failed to save attendance"));
    }
  };

  // -------- REPORT --------
  const handleGetReport = async () => {
    try {
      const res = await getReport(form.id);
      setReport(res.data);
      setMessage("📊 Report loaded successfully");
    } catch (err) {
      setMessage("❌ " + (err.response?.data?.detail || "Student not found"));
    }
  };

  return (
    <div>
      {/* MESSAGE */}
      {message && (
        <div
          className={`admin-message ${
            message.startsWith("✅") || message.startsWith("📊")
              ? "success"
              : "error"
          }`}
        >
          {message}
        </div>
      )}

      {/* ---------------- STUDENTS TAB ---------------- */}
      {mode === "students" && (
        <>
          <h3>📋 Students</h3>

          <input
            placeholder="Student ID"
            value={form.id}
            onChange={(e) => setForm({ ...form, id: e.target.value })}
          />

          <input
            placeholder="Name"
            value={form.name}
            onChange={(e) => setForm({ ...form, name: e.target.value })}
          />

          <button onClick={handleAddStudent}>Add</button>
          <button onClick={handleUpdateStudent}>Update</button>
          <button onClick={handleDeleteStudent}>Delete</button>

          <ul>
            {students.map((s) => (
              <li key={s.id}>
                {s.id} — {s.name}
              </li>
            ))}
          </ul>
        </>
      )}

      {/* ---------------- MARKS TAB ---------------- */}
      {mode === "marks" && (
        <>
          <h3>📝 Add Multiple Marks</h3>

          <input
            placeholder="Student ID"
            value={form.id}
            onChange={(e) => setForm({ ...form, id: e.target.value })}
          />

          {marks.map((m, i) => (
            <div key={i} style={{ display: "flex", gap: "10px" }}>
              <input
                placeholder="Subject"
                value={m.subject}
                onChange={(e) => updateMarks(i, "subject", e.target.value)}
              />
              <input
                placeholder="Score"
                value={m.score}
                onChange={(e) => updateMarks(i, "score", e.target.value)}
              />
            </div>
          ))}

          <button onClick={addMoreMarks}>➕ Add More</button>
          <button onClick={handleSaveMarks}>💾 Save All Marks</button>
        </>
      )}

      {/* ---------------- ATTENDANCE TAB ---------------- */}
      {mode === "attendance" && (
        <>
          <h3>📅 Attendance</h3>

          <input
            placeholder="Student ID"
            value={form.id}
            onChange={(e) => setForm({ ...form, id: e.target.value })}
          />

          <input
            type="date"
            value={attendance.date}
            onChange={(e) =>
              setAttendance({ ...attendance, date: e.target.value })
            }
          />

          <select
            value={attendance.status}
            onChange={(e) =>
              setAttendance({ ...attendance, status: e.target.value })
            }
          >
            <option value="Present">Present</option>
            <option value="Absent">Absent</option>
          </select>

          <button onClick={handleSaveAttendance}>
            💾 Save Attendance
          </button>
        </>
      )}

      {/* ---------------- REPORT TAB ---------------- */}
      {mode === "report" && (
        <>
          <h3>📊 Student Report</h3>

          <input
            placeholder="Student ID"
            value={form.id}
            onChange={(e) => setForm({ ...form, id: e.target.value })}
          />

          <button onClick={handleGetReport}>Get Report</button>

          {report && (
            <div style={{ marginTop: "10px", textAlign: "left" }}>
              <h4>Student</h4>
              <p>ID: {report.student.id}</p>
              <p>Name: {report.student.name}</p>

              <h4>Academics</h4>
              <ul>
                {report.academics.map((a, i) => (
                  <li key={i}>
                    {a.subject}: {a.score}
                  </li>
                ))}
              </ul>

              <h4>Attendance</h4>
              <ul>
                {report.attendance.map((a, i) => (
                  <li key={i}>
                    {a.date} — {a.status}
                  </li>
                ))}
              </ul>
            </div>
          )}
        </>
      )}
    </div>
  );
}

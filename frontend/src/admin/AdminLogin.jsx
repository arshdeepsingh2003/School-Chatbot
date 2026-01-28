import { useState } from "react";
import axios from "axios";

export default function AdminLogin({ onLogin }) {
  const [token, setToken] = useState("");
  const [message, setMessage] = useState("");
  const [loading, setLoading] = useState(false);

  const handleLogin = async () => {
    const cleanToken = token.trim();

    if (!cleanToken) {
      setMessage("❌ Enter admin token");
      return;
    }

    if (loading) return; // 🔥 prevent double requests

    setLoading(true);
    setMessage("");

    try {
      const res = await axios.get(
        `${import.meta.env.VITE_API_BASE_URL}/admin/check`,
        {
          headers: { "X-Admin-Token": cleanToken }
        }
      );

      if (res.status === 200) {
        localStorage.setItem("admin_token", cleanToken);
        setMessage("");
        onLogin(); // ✅ only success path opens dashboard
      }
    } catch {
      localStorage.removeItem("admin_token");
      setMessage("❌ Invalid admin token");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="admin-panel">
      <h2>🔐 Admin Login</h2>

      <input
        placeholder="Enter Admin Token"
        value={token}
        onChange={(e) => setToken(e.target.value)}
        onKeyDown={(e) => e.key === "Enter" && handleLogin()}
        disabled={loading}
      />

      <button onClick={handleLogin} disabled={loading}>
        {loading ? "Checking..." : "Login"}
      </button>

      {message && <p>{message}</p>}
    </div>
  );
}

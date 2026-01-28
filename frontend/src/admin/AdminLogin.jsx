import { useState } from "react";

export default function AdminLogin({ onLogin }) {
  const [token, setToken] = useState("");

  const handleLogin = () => {
    if (!token) {
      alert("Enter admin token");
      return;
    }

    localStorage.setItem("admin_token", token);
    onLogin();
  };

  return (
    <div className="admin-panel">
      <h2>🔐 Admin Login</h2>

      <input
        type="text"
        placeholder="Enter Admin Token"
        value={token}
        onChange={(e) => setToken(e.target.value)}
      />

      <button onClick={handleLogin}>
        Login
      </button>
    </div>
  );
}

import { useState } from "react";
import { sendMessage } from "../api";

export default function ChatBox({ role, studentId }) {
  const [message, setMessage] = useState("");
  const [chat, setChat] = useState([]);
  const [loading, setLoading] = useState(false);

  const handleSend = async () => {
    if (!message) return;

    const userMsg = { sender: "You", text: message };
    setChat((prev) => [...prev, userMsg]);

    setLoading(true);

    try {
      const payload = {
        message,
        role,
        student_id: studentId ? Number(studentId) : null
      };

      const res = await sendMessage(payload);

      const botMsg = { sender: "Bot", text: res.data.reply };
      setChat((prev) => [...prev, botMsg]);
    } catch (err) {
      setChat((prev) => [
        ...prev,
        { sender: "Bot", text: "Server error. Is backend running?" }
      ]);
    }

    setMessage("");
    setLoading(false);
  };

  return (
    <div className="chatbox">
      <div className="messages">
        {chat.map((msg, i) => (
          <div
            key={i}
            className={msg.sender === "You" ? "msg user" : "msg bot"}
          >
            <strong>{msg.sender}:</strong>
            <pre>{msg.text}</pre>
          </div>
        ))}
        {loading && <div className="msg bot">Bot is typing...</div>}
      </div>

      <div className="input-area">
        <input
          type="text"
          placeholder="Ask about marks, attendance, exams..."
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && handleSend()}
        />
        <button onClick={handleSend}>Send</button>
      </div>
    </div>
  );
}

import { useState, useEffect, useRef } from "react";
import { sendMessage } from "../api";

export default function ChatBox({ role, studentId }) {
  const [message, setMessage] = useState("");
  const [chat, setChat] = useState([]);
  const [loading, setLoading] = useState(false);
  const bottomRef = useRef(null);

  const handleSend = async () => {
    if (!message.trim()) return;

    const userMsg = { sender: "user", text: message };
    setChat((prev) => [...prev, userMsg]);
    setLoading(true);

    try {
      const payload = {
        message,
        role,
        student_id: studentId ? Number(studentId) : null
      };

      const res = await sendMessage(payload);

      const botMsg = { sender: "bot", text: res.data.reply };
      setChat((prev) => [...prev, botMsg]);
    } catch {
      setChat((prev) => [
        ...prev,
        { sender: "bot", text: "⚠️ Server error. Is backend running?" }
      ]);
    }

    setMessage("");
    setLoading(false);
  };

  // Auto scroll
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [chat, loading]);

  return (
    <div className="chatbox">
      <div className="messages">
        {chat.map((msg, i) => (
          <div key={i} className={`message-row ${msg.sender}`}>
            <div className="badge">
              {msg.sender === "user" ? "You" : "Bot"}
            </div>

            <div className={`msg ${msg.sender}`}>
              {msg.text}
            </div>
          </div>
        ))}

        {loading && (
          <div className="message-row bot">
            <div className="badge">Bot</div>
            <div className="msg bot typing">Typing...</div>
          </div>
        )}

        <div ref={bottomRef} />
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

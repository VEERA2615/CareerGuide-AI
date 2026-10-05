import { useState } from "react";
import { chat } from "../api.js";

export default function Chat({ resumeText = "", targetRole = "Data Analyst" }) {
  const [text, setText] = useState("");
  const [log, setLog] = useState([]);
  const [busy, setBusy] = useState(false);

  async function send() {
    if (!text.trim() || busy) return;

    const q = text.trim();

    setText("");
    setBusy(true);

    setLog((l) => [
      ...l,
      {
        who: "you",
        text: q,
      },
    ]);

    try {
      const r = await chat(q, resumeText, targetRole);

      setLog((l) => [
        ...l,
        {
          who: "ai",
          text: r.reply || "I couldn't generate a response.",
        },
      ]);
    } catch (e) {
      setLog((l) => [
        ...l,
        {
          who: "ai",
          text: e.message || "Something went wrong.",
        },
      ]);
    } finally {
      setBusy(false);
    }
  }

  return (
    <section className="panel">
      <h2>Ask the career agent</h2>

      {log.map((m, i) => (
        <div key={i} className={"msg " + m.who}>
          {m.text}
        </div>
      ))}

      <div className="row">
        <input
          value={text}
          onChange={(e) => setText(e.target.value)}
          placeholder="Am I ready for an AI Engineer role?"
          onKeyDown={(e) => {
            if (e.key === "Enter") {
              send();
            }
          }}
        />

        <button onClick={send} disabled={busy}>
          {busy ? "Thinking..." : "Ask"}
        </button>
      </div>
    </section>
  );
}
import { useState } from "react";
import { uploadResume } from "../api.js";

export default function Upload({ onDone, onError }) {
  const [busy, setBusy] = useState(false);
  const [skills, setSkills] = useState([]);

  async function pick(e) {
    const file = e.target.files[0];
    if (!file) return;
    setBusy(true); onError("");
    try {
      const d = await uploadResume(file);
      setSkills(d.profile.skills || []);
      onDone(d.resume_id);
    } catch (err) { onError(err.message); }
    setBusy(false);
  }

  return (
    <section className="panel">
      <label className="drop">
        {busy ? "Reading your resume..." : "Choose your resume (PDF)"}
        <input type="file" accept="application/pdf" onChange={pick} disabled={busy} />
      </label>
      {skills.length > 0 && (
        <p className="chips">Skills found: {skills.map((s) => <span key={s} className="chip">{s}</span>)}</p>
      )}
    </section>
  );
}

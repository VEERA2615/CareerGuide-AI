import React, { useMemo, useRef, useState } from "react";
import {
  ArrowRight, Bot, BriefcaseBusiness, Check, ChevronDown, CircleAlert,
  FileText, Flame, GraduationCap, Lightbulb, MessageCircle, Plus,
  RefreshCw, Send, Sparkles, Target, Trash2, Upload, X, Zap
} from "lucide-react";

const API = "http://localhost:8000";

const fallbackCareers = [
  "Data Analyst", "Business Analyst", "Data Scientist",
  "ML Engineer", "Product Analyst", "Data Engineer"
];

function App() {
  const [file, setFile] = useState(null);
  const [resumeText, setResumeText] = useState("");
  const [skills, setSkills] = useState([]);
  const [targetRole, setTargetRole] = useState("Data Analyst");
  const [analysis, setAnalysis] = useState(null);
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  const [dragging, setDragging] = useState(false);
  const [chat, setChat] = useState([]);
  const [message, setMessage] = useState("");
  const [newSkill, setNewSkill] = useState("");
  const fileInput = useRef(null);

  const readiness = analysis?.readiness_score ?? 0;
  const circumference = 2 * Math.PI * 52;
  const dash = circumference - (readiness / 100) * circumference;

  const suggested = useMemo(() => {
    const known = new Set(skills.map(s => s.toLowerCase()));
    return ["Python", "SQL", "Excel", "Power BI", "Statistics", "Machine Learning"]
      .filter(s => !known.has(s.toLowerCase()));
  }, [skills]);

  async function parseResponse(response) {
    const data = await response.json().catch(() => ({}));
    if (!response.ok) {
      throw new Error(data.detail || `Request failed (${response.status})`);
    }
    return data;
  }

  async function uploadResume(selected) {
    if (!selected) return;
    setError("");
    setAnalysis(null);
    setBusy(true);
    try {
      const form = new FormData();
      form.append("file", selected);
      const data = await parseResponse(await fetch(`${API}/resume`, { method: "POST", body: form }));
      setFile(selected);
      setResumeText(data.text);
      setSkills(data.skills || []);
    } catch (e) {
      setError(e.message);
      setFile(null);
    } finally {
      setBusy(false);
    }
  }

  function onDrop(e) {
    e.preventDefault();
    setDragging(false);
    uploadResume(e.dataTransfer.files?.[0]);
  }

  async function analyze() {
    if (!resumeText) {
      setError("Upload a readable resume first.");
      return;
    }
    setBusy(true);
    setError("");
    try {
      const data = await parseResponse(await fetch(`${API}/analyze`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ resume_text: resumeText, skills, target_role: targetRole })
      }));
      setAnalysis(data);
      window.scrollTo({ top: 520, behavior: "smooth" });
    } catch (e) {
      setError(e.message);
    } finally {
      setBusy(false);
    }
  }

  async function sendChat(e) {
    e?.preventDefault();
    const text = message.trim();
    if (!text || busy) return;
    setMessage("");
    setChat(prev => [...prev, { role: "user", text }]);
    setBusy(true);
    try {
      const data = await parseResponse(await fetch(`${API}/chat`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: text, resume_text: resumeText, target_role: targetRole })
      }));
      setChat(prev => [...prev, { role: "assistant", text: data.reply }]);
    } catch (e) {
      setChat(prev => [...prev, { role: "assistant", text: `I couldn't answer that yet: ${e.message}` }]);
    } finally {
      setBusy(false);
    }
  }

  function addSkill() {
    const value = newSkill.trim();
    if (value && !skills.some(s => s.toLowerCase() === value.toLowerCase())) {
      setSkills([...skills, value]);
    }
    setNewSkill("");
  }

  function removeSkill(skill) {
    setSkills(skills.filter(s => s !== skill));
  }

  return (
    <div className="app-shell">
      <header className="topbar">
        <div className="brand">
          <div className="brand-mark"><Sparkles size={19}/></div>
          <div><strong>CareerGuide</strong><span>AI</span></div>
        </div>
        <div className="top-status"><span className="status-dot"/> AI career copilot</div>
      </header>

      <main>
        <section className="hero">
          <div className="hero-copy">
            <div className="eyebrow"><Zap size={14}/> PERSONALIZED CAREER INTELLIGENCE</div>
            <h1>Turn your resume into a <em>career roadmap.</em></h1>
            <p>Upload your resume, choose your target role, and get a practical plan for the skills, projects, and actions that move you closer to your goal.</p>
            <div className="hero-pills">
              <span><Check size={14}/> Skill-gap analysis</span>
              <span><Check size={14}/> Project ideas</span>
              <span><Check size={14}/> Weekly roadmap</span>
            </div>
          </div>
          <div className="hero-orbit">
            <div className="orbit-card card-a"><Target size={17}/><span>Role fit</span><b>AI guided</b></div>
            <div className="orbit-card card-b"><GraduationCap size={17}/><span>Learning</span><b>Personalized</b></div>
            <div className="orbit-card card-c"><BriefcaseBusiness size={17}/><span>Projects</span><b>Portfolio-ready</b></div>
            <div className="hero-core"><Sparkles size={34}/><b>CG</b></div>
          </div>
        </section>

        {error && (
          <div className="alert">
            <CircleAlert size={20}/>
            <div><strong>Something needs attention</strong><span>{error}</span></div>
            <button onClick={() => setError("")}><X size={17}/></button>
          </div>
        )}

        <section className="workspace">
          <div className="setup-card panel">
            <div className="panel-title">
              <div><span className="number">01</span><div><h2>Build your profile</h2><p>Start with your current resume.</p></div></div>
              <FileText size={20}/>
            </div>

            <div
              className={`dropzone ${dragging ? "dragging" : ""} ${file ? "has-file" : ""}`}
              onDragOver={e => { e.preventDefault(); setDragging(true); }}
              onDragLeave={() => setDragging(false)}
              onDrop={onDrop}
              onClick={() => fileInput.current?.click()}
            >
              <input ref={fileInput} type="file" accept=".pdf,.docx,.txt" hidden onChange={e => uploadResume(e.target.files?.[0])}/>
              {file ? (
                <>
                  <div className="file-icon"><Check size={22}/></div>
                  <strong>{file.name}</strong>
                  <span>{Math.round(file.size / 1024)} KB · readable text extracted</span>
                  <button className="text-button" onClick={(e) => { e.stopPropagation(); setFile(null); setResumeText(""); setSkills([]); setAnalysis(null); }}>Replace resume</button>
                </>
              ) : (
                <>
                  <div className="upload-icon"><Upload size={22}/></div>
                  <strong>Drop your resume here</strong>
                  <span>PDF, DOCX or TXT · up to 8 MB</span>
                  <button className="upload-button" onClick={e => { e.stopPropagation(); fileInput.current?.click(); }}>Choose file <ArrowRight size={16}/></button>
                </>
              )}
            </div>

            <label className="field-label">Target career</label>
            <div className="select-wrap">
              <BriefcaseBusiness size={17}/>
              <select value={targetRole} onChange={e => setTargetRole(e.target.value)}>
                {fallbackCareers.map(role => <option key={role}>{role}</option>)}
              </select>
              <ChevronDown size={16}/>
            </div>

            <label className="field-label">Your skills <span>edit after resume scan</span></label>
            <div className="skills-box">
              {skills.map(skill => (
                <button className="skill-chip" key={skill} onClick={() => removeSkill(skill)}>{skill}<X size={12}/></button>
              ))}
              <div className="skill-add">
                <input value={newSkill} onChange={e => setNewSkill(e.target.value)} onKeyDown={e => e.key === "Enter" && addSkill()} placeholder="Add skill..." />
                <button onClick={addSkill}><Plus size={14}/></button>
              </div>
            </div>
            <div className="suggestions">
              {suggested.slice(0, 4).map(s => <button key={s} onClick={() => setSkills([...skills, s])}><Plus size={12}/>{s}</button>)}
            </div>

            <button className="primary-button full" onClick={analyze} disabled={busy || !resumeText}>
              {busy ? <><RefreshCw className="spin" size={17}/> Working...</> : <><Sparkles size={17}/> Analyze my career</>}
            </button>
          </div>

          <div className="preview-card panel">
            <div className="panel-title">
              <div><span className="number">02</span><div><h2>AI career analysis</h2><p>Your results appear here.</p></div></div>
              <Bot size={20}/>
            </div>

            {!analysis ? (
              <div className="empty-state">
                <div className="empty-orb"><Sparkles size={30}/></div>
                <h3>Ready when you are</h3>
                <p>Upload your resume and run the analysis. CareerGuide will turn your current skills into a clear next-step strategy.</p>
                <div className="mini-grid">
                  <div><Target size={17}/><b>Readiness</b><span>0–100 score</span></div>
                  <div><Lightbulb size={17}/><b>Skill gaps</b><span>Prioritized</span></div>
                  <div><Flame size={17}/><b>Today's action</b><span>Immediate step</span></div>
                </div>
              </div>
            ) : (
              <div className="analysis-preview">
                <div className="score-row">
                  <div className="score-ring">
                    <svg viewBox="0 0 120 120">
                      <circle className="ring-bg" cx="60" cy="60" r="52"/>
                      <circle className="ring-value" cx="60" cy="60" r="52" strokeDasharray={circumference} strokeDashoffset={dash}/>
                    </svg>
                    <div><b>{readiness}</b><span>/100</span></div>
                  </div>
                  <div><span className="eyebrow">READINESS FOR {targetRole.toUpperCase()}</span><h3>{analysis.headline}</h3><p>{analysis.summary}</p></div>
                </div>
                <div className="stat-grid">
                  <div><b>{analysis.strengths?.length || 0}</b><span>Strengths</span></div>
                  <div><b>{analysis.skill_gaps?.length || 0}</b><span>Skill gaps</span></div>
                  <div><b>{analysis.projects?.length || 0}</b><span>Projects</span></div>
                </div>
                <div className="preview-list">
                  {(analysis.skill_gaps || []).slice(0, 3).map(g => <div key={g.skill}><span>{g.skill}</span><small>{g.importance}</small></div>)}
                </div>
              </div>
            )}
          </div>
        </section>

        {analysis && (
          <>
            <section className="section-head">
              <div><span className="eyebrow">03 · YOUR STRATEGY</span><h2>From current skills to job-ready.</h2></div>
              <p>Follow the sequence instead of trying to learn everything at once.</p>
            </section>

            <section className="roadmap">
              {(analysis.roadmap || []).map((phase, i) => (
                <article className="road-card" key={phase.phase || i}>
                  <div className="road-number">{String(i + 1).padStart(2, "0")}</div>
                  <div className="road-content">
                    <div className="road-meta"><span>{phase.weeks}</span><span>{phase.phase}</span></div>
                    <h3>{phase.title}</h3><p>{phase.goal}</p>
                    <div className="topic-list">{(phase.topics || []).map(t => <span key={t}><Check size={13}/>{t}</span>)}</div>
                    <div className="project-callout"><Lightbulb size={18}/><div><b>Build:</b> {phase.project}<small>Deliverable: {phase.deliverable}</small></div></div>
                  </div>
                </article>
              ))}
            </section>

            <section className="lower-grid">
              <div className="today panel dark-panel">
                <div className="eyebrow">⚡ DO THIS TODAY</div>
                <h2>{analysis.today?.title}</h2>
                <p>{analysis.today?.time}</p>
                <ol>{(analysis.today?.steps || []).map((s, i) => <li key={s}><span>{i + 1}</span>{s}</li>)}</ol>
              </div>
              <div className="gaps panel">
                <div className="panel-title compact"><div><h2>Highest-impact gaps</h2><p>Learn these before lower-priority topics.</p></div></div>
                <div className="gap-list">
                  {(analysis.skill_gaps || []).map(g => <div className="gap-item" key={g.skill}><div><b>{g.skill}</b><p>{g.reason}</p></div><span className={`importance ${String(g.importance).toLowerCase()}`}>{g.importance}</span></div>)}
                </div>
              </div>
            </section>

            <section className="section-head project-head">
              <div><span className="eyebrow">04 · PORTFOLIO</span><h2>Projects that prove the skill.</h2></div>
            </section>
            <section className="project-grid">
              {(analysis.projects || []).map((p, i) => <article className="project-card" key={p.title || i}><div className="project-icon"><BriefcaseBusiness size={19}/></div><h3>{p.title}</h3><p>{p.why}</p><div>{(p.stack || []).map(s => <span key={s}>{s}</span>)}</div></article>)}
            </section>
          </>
        )}

        <section className="chat-section">
          <div className="section-head">
            <div><span className="eyebrow">05 · ASK CAREERGUIDE</span><h2>Your AI career copilot.</h2></div>
            <p>Ask about learning order, projects, interviews, skills, or your target role.</p>
          </div>
          <div className="chat-card panel">
            <div className="chat-messages">
              {chat.length === 0 ? (
                <div className="chat-empty"><div className="chat-avatar"><Bot size={22}/></div><div><b>What should I learn first?</b><p>Try: “I have 8 weeks. Give me a Data Analyst study plan.”</p></div></div>
              ) : chat.map((m, i) => <div className={`message ${m.role}`} key={i}><div className="message-avatar">{m.role === "assistant" ? <Bot size={15}/> : "You"}</div><div>{m.text}</div></div>)}
            </div>
            <form className="chat-form" onSubmit={sendChat}>
              <input value={message} onChange={e => setMessage(e.target.value)} placeholder="Ask CareerGuide anything..." />
              <button disabled={busy || !message.trim()}><Send size={17}/></button>
            </form>
          </div>
        </section>
      </main>

      <footer><div className="brand"><div className="brand-mark"><Sparkles size={16}/></div><strong>CareerGuide AI</strong></div><span>Built for practical career progress · v3.0</span></footer>
    </div>
  );
}

export default App;

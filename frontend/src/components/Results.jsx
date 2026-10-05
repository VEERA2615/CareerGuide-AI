const List = ({ items = [], cls }) => (
  <p className="chips">{items.length ? items.map((s) => <span key={s} className={"chip " + cls}>{s}</span>) : "None"}</p>
);

export default function Results({ gap, plan }) {
  const unique = [...new Set((gap.sources || []).map((s) => `${s.source} (page ${s.page})`))];
  return (
    <section className="panel">
      <h2>{gap.target_role}</h2>
      <div className="score"><strong>{Math.round(gap.match_score)}%</strong> match</div>
      <h3>You already have</h3><List items={gap.skills_present} cls="ok" />
      <h3>Partly there</h3><List items={gap.skills_partial} cls="mid" />
      <h3>Still to learn</h3><List items={gap.skill_gaps} cls="gap" />

      <h3>Your roadmap</h3>
      <ol className="road">
        {(plan.months || []).map((m, i) => (
          <li key={i}><b>{m.title}</b><br />{(m.topics || []).join(", ")}</li>
        ))}
      </ol>
      {plan.projects?.length > 0 && <p><b>Projects to build:</b> {plan.projects.join(", ")}</p>}
      {unique.length > 0 && <p className="src">Sources: {unique.join("; ")}</p>}
    </section>
  );
}

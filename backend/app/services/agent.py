import json
from sqlalchemy.orm import Session
from ..database import Resume, Analysis
from . import llm, rag


def _profile(db, resume_id):
    r = db.get(Resume, resume_id)
    return json.loads(r.profile_json) if r else {}


def tool_search_careers(query, **_):
    return rag.search(query, k=5)


def tool_skill_gap(db, resume_id, target_role, **_):
    prof, docs = _profile(db, resume_id), rag.search(f"{target_role} required skills", k=5)
    ctx = "\n\n".join(f"[{d['source']} p{d['page']}] {d['text']}" for d in docs)
    res = llm.ask_json(
        "You compare a student's skills to a role using ONLY the context. Return JSON: match_score (0-100), "
        "skills_present (list), skills_partial (list), skill_gaps (list).",
        f"Role: {target_role}\nStudent skills: {prof.get('skills', [])}\nContext:\n{ctx}",
    )
    res["target_role"] = target_role
    res["sources"] = [{"source": d["source"], "page": d["page"]} for d in docs]
    db.add(Analysis(resume_id=resume_id, target_role=target_role, match_score=float(res.get("match_score", 0)),
                    result_json=json.dumps(res)))
    db.commit()
    return res


def tool_roadmap(db, resume_id, target_role, **_):
    prof, docs = _profile(db, resume_id), rag.search(f"{target_role} learning roadmap projects", k=4)
    ctx = "\n\n".join(d["text"] for d in docs)
    return llm.ask_json(
        "Make a learning roadmap. Return JSON: months (list of {title, topics (list)}), projects (list).",
        f"Role: {target_role}\nStudent skills: {prof.get('skills', [])}\nContext:\n{ctx}",
    )


def tool_recommend(db, resume_id, interests="", **_):
    prof = _profile(db, resume_id)
    docs = rag.search(f"careers for {interests} {prof.get('skills', [])}", k=5)
    ctx = "\n\n".join(f"[{d['career']}] {d['text']}" for d in docs)
    return llm.ask_json(
        "Recommend the top 3 careers. Return JSON: recommendations (list of {role, reason}).",
        f"Interests: {interests}\nProfile: {prof}\nContext:\n{ctx}",
    )


def _fn(name, desc, props, req):
    return {"type": "function", "function": {"name": name, "description": desc,
            "parameters": {"type": "object", "properties": props, "required": req}}}


S = {"type": "string"}
TOOLS = [
    _fn("search_careers", "Search the career knowledge base.", {"query": S}, ["query"]),
    _fn("skill_gap", "Compare resume skills to a target role.", {"target_role": S}, ["target_role"]),
    _fn("roadmap", "Make a learning roadmap for a role.", {"target_role": S}, ["target_role"]),
    _fn("recommend", "Recommend careers from interests and resume.", {"interests": S}, []),
]


def run_agent(db: Session, resume_id: int, message: str) -> dict:
    registry = {"search_careers": tool_search_careers, "skill_gap": tool_skill_gap,
                "roadmap": tool_roadmap, "recommend": tool_recommend}
    messages = [
        {"role": "system", "content": "You are CareerGuide AI, a friendly career coach for students. Use tools to "
         "get facts instead of guessing. Answer simply and mention which documents your facts came from."},
        {"role": "user", "content": message},
    ]
    used = []
    for _ in range(5):
        msg = llm.chat(messages, tools=TOOLS, tool_choice="auto").choices[0].message
        if not msg.tool_calls:
            return {"answer": msg.content, "tools_used": used}
        messages.append(msg.model_dump(exclude_none=True))
        for tc in msg.tool_calls:
            args = json.loads(tc.function.arguments or "{}")
            used.append(tc.function.name)
            try:
                out = registry[tc.function.name](db=db, resume_id=resume_id, **args)
            except Exception as e:
                out = {"error": str(e)}
            messages.append({"role": "tool", "tool_call_id": tc.id, "content": json.dumps(out)[:6000]})
    return {"answer": "Sorry, I could not finish. Try a simpler question.", "tools_used": used}

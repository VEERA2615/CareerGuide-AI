const BASE = import.meta.env.VITE_API_URL || "http://localhost:8000";

async function call(path, options) {
  let res;

  try {
    res = await fetch(BASE + path, options);
  } catch {
    throw new Error(
      "Cannot reach the backend. Start it in the first terminal and try again."
    );
  }

  const data = await res.json().catch(() => ({}));

  if (!res.ok) {
    throw new Error(data.detail || "Something went wrong.");
  }

  return data;
}

const post = (path, body) =>
  call(path, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(body),
  });

export const getCareers = () => call("/careers");

export const uploadResume = (file) => {
  const f = new FormData();
  f.append("file", file);

  return call("/resume", {
    method: "POST",
    body: f,
  });
};

export const analyze = (skills, career) =>
  post("/analyze", { skills, career });

export const chat = (message, resumeText = "", targetRole = "Data Analyst") =>
  post("/chat", {
    message,
    resume_text: resumeText,
    target_role: targetRole,
  });
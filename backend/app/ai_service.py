import os
import json
import re
from typing import Any, Dict

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()


class GeminiServiceError(Exception):
    """Kept for compatibility with main.py."""
    pass


class GeminiService:

    def __init__(self):
        self.api_key = os.getenv("OPENROUTER_API_KEY")

        if not self.api_key:
            raise GeminiServiceError(
                "OPENROUTER_API_KEY is missing. Add it to backend/.env"
            )

        self.model = os.getenv(
            "OPENROUTER_MODEL",
            "openrouter/free"
        )

        self.configured = True

        self.client = OpenAI(
            api_key=self.api_key,
            base_url="https://openrouter.ai/api/v1",
        )

    def _generate(self, prompt: str) -> str:
        print(f"[CareerGuide AI] Calling OpenRouter: {self.model}")

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are CareerGuide AI, an expert career advisor "
                            "for students and early-career professionals. "
                            "Give practical, realistic and evidence-based "
                            "career guidance. Never invent skills or experience "
                            "that are not present in the resume."
                        ),
                    },
                    {
                        "role": "user",
                        "content": prompt,
                    },
                ],
                temperature=0.2,
                max_tokens=5000,
            )

            if not response.choices:
                raise GeminiServiceError(
                    "OpenRouter returned an empty response."
                )

            content = response.choices[0].message.content

            if not content:
                raise GeminiServiceError(
                    "OpenRouter returned no text."
                )

            print("[CareerGuide AI] OpenRouter response received.")

            return content.strip()

        except Exception as exc:
            error_text = str(exc)

            print(f"[CareerGuide AI] OpenRouter error: {error_text}")

            if "401" in error_text or "authentication" in error_text.lower():
                raise GeminiServiceError(
                    "OpenRouter API key is invalid or unauthorized."
                ) from exc

            if "429" in error_text:
                raise GeminiServiceError(
                    "OpenRouter free-model rate limit reached. Please try again later."
                ) from exc

            if "402" in error_text:
                raise GeminiServiceError(
                    "OpenRouter requires credits for the selected model."
                ) from exc

            if "404" in error_text:
                raise GeminiServiceError(
                    f"OpenRouter model '{self.model}' was not found."
                ) from exc

            if "503" in error_text or "502" in error_text:
                raise GeminiServiceError(
                    "OpenRouter/provider is temporarily unavailable. Please try again."
                ) from exc

            raise GeminiServiceError(
                f"OpenRouter request failed: {type(exc).__name__}"
            ) from exc

    def _extract_json(self, text: str) -> Dict[str, Any]:

        text = text.strip()

        # Remove markdown JSON fences
        text = re.sub(
            r"^```(?:json)?\s*",
            "",
            text,
            flags=re.IGNORECASE
        )

        text = re.sub(
            r"\s*```$",
            "",
            text
        )

        # First attempt: entire response is JSON
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            pass

        # Second attempt: find the first JSON object
        start = text.find("{")
        end = text.rfind("}")

        if start != -1 and end != -1 and end > start:
            candidate = text[start:end + 1]

            try:
                return json.loads(candidate)
            except json.JSONDecodeError:
                pass

        raise GeminiServiceError(
            "OpenRouter returned an invalid analysis format."
        )

    def analyze_resume(
        self,
        resume_text: str,
        skills: list[str],
        target_role: str,
    ) -> Dict[str, Any]:

        prompt = f"""
Analyze this candidate for the target career role.

TARGET ROLE:
{target_role}

DECLARED SKILLS:
{", ".join(skills) if skills else "None provided"}

RESUME:
{resume_text}

You MUST return ONLY valid JSON.

Do not use markdown.
Do not use ```json.
Do not add explanations outside the JSON.

Use exactly this structure:

{{
  "readiness_score": 0,
  "headline": "Short assessment headline",
  "summary": "2-3 sentence candidate summary",

  "strengths": [
    {{
      "skill": "Skill name",
      "reason": "Why this is a strength"
    }}
  ],

  "skill_gaps": [
    {{
      "skill": "Skill name",
      "importance": "High",
      "reason": "Why the candidate needs this skill"
    }}
  ],

  "roadmap": [
    {{
      "phase": "Phase 1",
      "weeks": "Weeks 1-2",
      "title": "Foundation",
      "goal": "What the candidate should achieve",
      "topics": ["Topic 1", "Topic 2", "Topic 3"],
      "project": "Project to build",
      "deliverable": "What should be completed"
    }},
    {{
      "phase": "Phase 2",
      "weeks": "Weeks 3-4",
      "title": "Applied Skills",
      "goal": "What the candidate should achieve",
      "topics": ["Topic 1", "Topic 2"],
      "project": "Project to build",
      "deliverable": "What should be completed"
    }},
    {{
      "phase": "Phase 3",
      "weeks": "Weeks 5-6",
      "title": "Portfolio",
      "goal": "What the candidate should achieve",
      "topics": ["Topic 1", "Topic 2"],
      "project": "Project to build",
      "deliverable": "What should be completed"
    }}
  ],

  "today": {{
    "title": "Most important action today",
    "time": "2 hours",
    "steps": [
      "Step 1",
      "Step 2",
      "Step 3"
    ]
  }},

  "projects": [
    {{
      "title": "Project name",
      "why": "Why this project proves the required skill",
      "stack": ["Python", "SQL", "Power BI"]
    }},
    {{
      "title": "Second project",
      "why": "Why this project is useful",
      "stack": ["Python", "SQL"]
    }}
  ]
}}

IMPORTANT RULES:

1. readiness_score must be an integer from 0 to 100.
2. Base the score on the actual resume and declared skills.
3. Do not invent experience.
4. Give at least 3 strengths when evidence exists.
5. Give at least 3 skill gaps.
6. Give at least 3 roadmap phases.
7. Give at least 2 projects.
8. Make the recommendations specific to the target role.
9. Prioritize skills that improve employability.
10. Keep the advice realistic for a student or early-career candidate.
"""

        raw = self._generate(prompt)

        data = self._extract_json(raw)

        # Defensive defaults so the React UI never crashes
        result = {
            "readiness_score": int(data.get("readiness_score", 0)),
            "headline": data.get(
                "headline",
                "Your career assessment is ready."
            ),
            "summary": data.get(
                "summary",
                "CareerGuide analyzed your resume and identified your next steps."
            ),
            "strengths": data.get("strengths", []),
            "skill_gaps": data.get("skill_gaps", []),
            "roadmap": data.get("roadmap", []),
            "today": data.get("today", {
                "title": "Start with your highest-impact skill gap",
                "time": "2 hours",
                "steps": [
                    "Choose one priority skill.",
                    "Study the fundamentals.",
                    "Build a small practical exercise."
                ]
            }),
            "projects": data.get("projects", []),
            "model": self.model,
            "provider": "OpenRouter",
        }

        # Keep score inside valid range
        result["readiness_score"] = max(
            0,
            min(100, result["readiness_score"])
        )

        print(
            f"[CareerGuide AI] Analysis ready: "
            f"{result['readiness_score']}/100"
        )

        return result

    def chat(
        self,
        message: str,
        resume_text: str = "",
        target_role: str = "Data Analyst",
    ) -> str:

        prompt = f"""
You are CareerGuide AI.

TARGET CAREER:
{target_role}

CANDIDATE RESUME:
{resume_text if resume_text else "No resume provided."}

USER QUESTION:
{message}

Give practical career advice specifically for this candidate.

Focus on:
- what to learn
- what to build
- interview preparation
- skill priorities
- realistic timelines
- career decisions

Do not invent information about the candidate.

Use clear headings and bullet points when helpful.
"""

        return self._generate(prompt)

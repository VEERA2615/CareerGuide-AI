import json
from openai import OpenAI
from ..config import settings

client = OpenAI(api_key=settings.LLM_API_KEY or "missing", base_url=settings.LLM_BASE_URL)


def chat(messages, **kwargs):
    return client.chat.completions.create(model=settings.LLM_MODEL, messages=messages, temperature=0.2, **kwargs)


def ask_json(system: str, user: str) -> dict:
    r = chat(
        [{"role": "system", "content": system + " Reply with valid JSON only."}, {"role": "user", "content": user}],
        response_format={"type": "json_object"},
    )
    text = r.choices[0].message.content.strip().replace("```json", "").replace("```", "")
    return json.loads(text)

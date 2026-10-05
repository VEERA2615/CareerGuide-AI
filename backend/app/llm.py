import json, os, re, time
from dotenv import load_dotenv
from openai import OpenAI, RateLimitError, AuthenticationError

load_dotenv()
_client = OpenAI(api_key=os.getenv("LLM_API_KEY") or "missing", base_url=os.getenv("LLM_BASE_URL") or None)
MODEL = os.getenv("LLM_MODEL", "gemini-2.5-flash")


class LLMError(Exception):
    pass


def ask(messages, temperature=0.4):
    """Send chat messages, retry once on rate limit, return text."""
    for attempt in range(2):
        try:
            r = _client.chat.completions.create(model=MODEL, messages=messages, temperature=temperature)
            return (r.choices[0].message.content or "").strip()
        except RateLimitError:
            if attempt == 0:
                time.sleep(8)
                continue
            raise LLMError("Rate limit reached. Wait 60 seconds and try again.")
        except AuthenticationError:
            raise LLMError("API key rejected. Check LLM_API_KEY in backend/.env and restart the backend.")
        except Exception as e:
            raise LLMError(f"AI request failed: {str(e)[:200]}")


def ask_json(messages):
    text = ask(messages, temperature=0.3)
    text = re.sub(r"^```(?:json)?|```$", "", text.strip(), flags=re.M).strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        m = re.search(r"\{.*\}", text, re.S)
        if m:
            try:
                return json.loads(m.group(0))
            except json.JSONDecodeError:
                pass
        raise LLMError("The AI reply was not valid JSON. Click Analyze again.")

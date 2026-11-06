"""U2 - LLM calls: spec creation and candidate generation (Groq or Gemini via REST)."""
import re
import time
import requests
from config.settings import provider, api_key, model_name, NUM_CANDIDATES
from prompting.prompt_builder import SPEC_REQUEST, basic_prompt
from utils.helpers import extract_code, extract_json, DEFAULT_CONSTRAINTS


class LLMError(Exception):
    """Friendly error that is safe to show to the user (never contains the API key)."""


def call_llm(prompt, temperature=0.3):
    key = api_key()
    if not key:
        raise LLMError("No API key found. Add GROQ_API_KEY (or GEMINI_API_KEY) in the app secrets.")
    for attempt in range(3):
        try:
            if provider() == "gemini":
                url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name()}:generateContent"
                r = requests.post(url, headers={"x-goog-api-key": key}, timeout=90, json={
                    "contents": [{"parts": [{"text": prompt}]}],
                    "generationConfig": {"temperature": temperature}})
            else:
                r = requests.post("https://api.groq.com/openai/v1/chat/completions",
                                  headers={"Authorization": f"Bearer {key}"}, timeout=90, json={
                                      "model": model_name(), "temperature": temperature,
                                      "messages": [{"role": "user", "content": prompt}]})
        except requests.Timeout:
            raise LLMError("The AI service took too long to respond. Please try again.")
        except requests.RequestException:
            raise LLMError("Could not reach the AI service. Check your internet connection.")
        if r.status_code in (400, 401, 403) and "key" in r.text.lower():
            raise LLMError("The API key is invalid or not allowed. Please check the secret.")
        if r.status_code == 429 and attempt < 2:
            time.sleep(4 * (attempt + 1))
            continue
        if r.status_code == 429:
            raise LLMError("Rate limit reached on the free AI plan. Wait a minute and try again.")
        if r.status_code >= 400:
            raise LLMError(f"The AI service returned an error ({r.status_code}).")
        break
    try:
        data = r.json()
        if provider() == "gemini":
            return data["candidates"][0]["content"]["parts"][0]["text"]
        return data["choices"][0]["message"]["content"]
    except Exception:
        raise LLMError("The AI service sent an unexpected reply. Please try again.")


def make_spec(problem):
    """Ask the LLM to create function name, signature, constraints and visible/hidden tests."""
    reply = call_llm(SPEC_REQUEST.format(problem=problem), temperature=0.2)
    try:
        d = extract_json(reply)
        fn = d["function_name"]
        if not re.fullmatch(r"[A-Za-z_]\w*", fn):
            raise ValueError("bad function name")
        visible = [[str(e), x] for e, x in d["visible_tests"]]
        hidden = [[str(e), x] for e, x in d["hidden_tests"]]
        if not visible or not hidden:
            raise ValueError("no tests")
        return {"problem": problem, "fn": fn, "signature": d["signature"], "returns": d["returns"],
                "constraints": d.get("constraints") or DEFAULT_CONSTRAINTS,
                "visible": visible, "hidden": hidden}
    except Exception:
        raise LLMError("The AI could not understand that task well enough. Try describing it more clearly.")


def generate_candidates(prompt, n=NUM_CANDIDATES):
    """Several candidate solutions: same prompt, different temperatures."""
    temps = [0.2, 0.7, 1.0, 0.5, 0.9][:n]
    codes, last_error = [], None
    for t in temps:
        try:
            code = extract_code(call_llm(prompt, temperature=t))
        except LLMError as e:
            last_error = e
            if "key" in str(e).lower():
                raise
            continue
        if code.strip():
            codes.append(code)
    if not codes:
        raise last_error or LLMError("The AI returned empty code. Please try again.")
    return codes


def generate_basic(problem):
    return extract_code(call_llm(basic_prompt(problem), temperature=0.2))

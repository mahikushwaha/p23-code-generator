import json
import re
from pathlib import Path

TASKS_FILE = Path(__file__).resolve().parent.parent / "evaluation" / "tasks.json"
DEFAULT_CONSTRAINTS = [
    "Handle edge cases (empty input, single element, zero, negatives) correctly.",
    "Return the value; do not print anything.",
    "Keep it simple and readable.",
]


def extract_code(text):
    """Pull Python code out of an LLM reply (handles ```python fences)."""
    if not text:
        return ""
    blocks = re.findall(r"```(?:python|py)?\s*\n(.*?)```", text, flags=re.S | re.I)
    code = max(blocks, key=len) if blocks else text
    return code.strip()


def extract_json(text):
    text = re.sub(r"```(?:json)?", "", text or "")
    start, end = text.find("{"), text.rfind("}")
    if start == -1 or end == -1:
        raise ValueError("No JSON found in the AI reply")
    return json.loads(text[start:end + 1])


def load_tasks():
    with open(TASKS_FILE, encoding="utf-8") as f:
        return json.load(f)


def task_to_spec(t):
    return {"problem": t["problem"], "fn": t["fn"], "signature": t["sig"], "returns": t["returns"],
            "constraints": DEFAULT_CONSTRAINTS, "visible": t["visible"], "hidden": t["hidden"]}

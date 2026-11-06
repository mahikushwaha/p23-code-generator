"""U2 - one automatic repair using the error message and failed test."""
from llm.generator import call_llm, LLMError
from utils.helpers import extract_code


def build_repair_prompt(spec, code, run):
    if run["failures"]:
        f = run["failures"][0]
        failed = (f"Test: {f['expr']}\nExpected output: {f['expected']!r}\n"
                  f"Actual output: {f['actual']!r}\nError: {f['error'] or 'none (wrong answer)'}")
    else:
        failed = f"No test could run. Error: {run['error']}"
    return f"""The Python code below failed its tests. Fix it.

## Original problem
{spec['problem']}

## Required function
{spec['signature']}

## Generated code
```python
{code}
```

## Failure details
{failed}

Reply with ONE corrected ```python code block only. Keep the same function name. No explanation."""


def repair_once(spec, code, run):
    """Called at most once per task (no loop)."""
    fixed = extract_code(call_llm(build_repair_prompt(spec, code, run), temperature=0.2))
    if not fixed.strip():
        raise LLMError("The AI returned empty code for the repair.")
    return fixed

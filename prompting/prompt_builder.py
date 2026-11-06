"""U1 - Prompt engineering: a basic prompt vs a structured prompt."""
import json
from config.settings import ALLOWED_IMPORTS


def basic_prompt(problem):
    """Technique 1: simple direct request."""
    return f"Write Python code for this task:\n{problem}"


def structured_prompt(spec):
    """Technique 2: specification + input/output + examples + constraints + safety."""
    examples = "\n".join(f"  {expr}  ->  {json.dumps(exp)}" for expr, exp in spec["visible"])
    constraints = "\n".join(f"- {c}" for c in spec["constraints"])
    return f"""You are an expert Python engineer.

## Problem specification
{spec['problem']}

## Programming language
Python 3 (use PyTorch only if the task needs it).

## Required function (name must match exactly)
{spec['signature']}

## Input format
Arguments exactly as in the signature above.

## Expected output
{spec['returns']}

## Examples
{examples}

## Constraints
{constraints}

## Safety restrictions
- No network, file, shell, or OS access. Do not use eval, exec, open or subprocess.
- Only import from: {', '.join(sorted(ALLOWED_IMPORTS))}.

## Output format
Reply with ONE ```python code block only. No explanation, no example calls, no print statements."""


SPEC_REQUEST = """Turn this programming request into a JSON test spec.
Request: {problem}

Return ONLY JSON with these keys:
- "function_name": snake_case name
- "signature": e.g. "def is_prime(n: int) -> bool"
- "returns": one sentence describing the return value
- "constraints": list of 2-3 short strings
- "visible_tests": 3 tests
- "hidden_tests": 4-6 tests including edge cases
Each test is [python_call_expression_as_string, expected_value]. Expected values must be JSON
(true/false, numbers, strings, lists, objects, null; tuples become lists). Round floats inside the
expression, e.g. "round(f(2),3)". For PyTorch tasks test shapes/values, e.g. "tuple(f(x).shape)" -> [4, 8].
Only use the function name in expressions (torch is available for PyTorch tests)."""

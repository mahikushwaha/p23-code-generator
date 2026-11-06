"""U4 - restricted execution: AST check, separate process, temp dir, clean env, limits, timeout."""
import ast
import json
import os
import subprocess
import sys
import tempfile
import time
from config.settings import ALLOWED_IMPORTS, BLOCKED_CALLS

HARNESS = r'''
import json, sys
meta = json.load(open("meta.json"))
if meta["needs_torch"]:
    import torch
import socket
class _NoNet(socket.socket):
    def __init__(self, *a, **k):
        raise RuntimeError("Network access is disabled in the sandbox")
socket.socket = _NoNet
ns = {"__name__": "solution"}
if meta["needs_torch"]:
    ns["torch"] = torch
out = {"load_error": None, "results": []}
try:
    exec(compile(open("solution.py").read(), "solution.py", "exec"), ns)
    if meta["fn"] not in ns:
        out["load_error"] = "Required function '%s' was not defined" % meta["fn"]
except BaseException as e:
    out["load_error"] = "%s: %s" % (type(e).__name__, e)
if not out["load_error"]:
    for t in meta["tests"]:
        r = {"id": t["id"], "passed": False, "actual": None, "error": None}
        try:
            actual = eval(t["expr"], ns)
            actual = json.loads(json.dumps(actual, default=str))
            r["actual"] = actual
            r["passed"] = actual == t["expected"]
        except BaseException as e:
            r["error"] = "%s: %s" % (type(e).__name__, str(e)[:200])
        out["results"].append(r)
print("@@RESULT@@" + json.dumps(out))
'''


def check_code_safety(code):
    """Static check before running. Returns an error message or None."""
    if not code.strip():
        return "The generated code is empty."
    try:
        tree = ast.parse(code)
    except SyntaxError as e:
        return f"Syntax error on line {e.lineno}: {e.msg}"
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            mods = [a.name.split(".")[0] for a in node.names]
        elif isinstance(node, ast.ImportFrom):
            mods = [(node.module or "").split(".")[0]]
        else:
            mods = []
        for m in mods:
            if m not in ALLOWED_IMPORTS:
                return f"Blocked import '{m}' (not in the allowed list)."
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id in BLOCKED_CALLS:
            return f"Blocked call '{node.func.id}()' (not allowed in the sandbox)."
    return None


def _limits(use_ram_limit):
    def apply():
        import resource
        resource.setrlimit(resource.RLIMIT_CPU, (60, 60))
        resource.setrlimit(resource.RLIMIT_FSIZE, (1_000_000, 1_000_000))
        if use_ram_limit:
            resource.setrlimit(resource.RLIMIT_AS, (2 * 1024 ** 3, 2 * 1024 ** 3))
    return apply


def run_sandboxed(code, fn, tests):
    """Run the code and tests in a throw-away process. Returns {status, error, results, time}."""
    start = time.time()
    problem = check_code_safety(code)
    if problem:
        return {"status": "blocked", "error": problem, "results": [], "time": 0.0}
    needs_torch = "torch" in code or any("torch" in t["expr"] for t in tests)
    timeout = 40 if needs_torch else 10
    with tempfile.TemporaryDirectory() as d:
        open(os.path.join(d, "solution.py"), "w", encoding="utf-8").write(code)
        open(os.path.join(d, "harness.py"), "w", encoding="utf-8").write(HARNESS)
        json.dump({"fn": fn, "tests": tests, "needs_torch": needs_torch}, open(os.path.join(d, "meta.json"), "w"))
        env = {"PATH": os.environ.get("PATH", ""), "HOME": d, "OMP_NUM_THREADS": "1",
               "PYTHONDONTWRITEBYTECODE": "1", "PYTHONHASHSEED": "0"}
        try:
            p = subprocess.run([sys.executable, "-I", "harness.py"], cwd=d, env=env, capture_output=True,
                               text=True, timeout=timeout,
                               preexec_fn=_limits(not needs_torch) if os.name == "posix" else None)
        except subprocess.TimeoutExpired:
            return {"status": "timeout", "error": f"Timed out after {timeout}s - possible infinite loop.",
                    "results": [], "time": round(time.time() - start, 2)}
        except Exception:
            return {"status": "crash", "error": "The sandbox could not start.", "results": [],
                    "time": round(time.time() - start, 2)}
    elapsed = round(time.time() - start, 2)
    line = next((l for l in reversed(p.stdout.splitlines()) if l.startswith("@@RESULT@@")), None)
    if not line:
        return {"status": "crash", "error": (p.stderr.strip()[-400:] or "The code crashed."),
                "results": [], "time": elapsed}
    data = json.loads(line[len("@@RESULT@@"):])
    if data["load_error"]:
        return {"status": "error", "error": data["load_error"], "results": [], "time": elapsed}
    return {"status": "ok", "error": None, "results": data["results"], "time": elapsed}


def hallucination_flags(code, fn):
    """Measured hallucination check: invented/unapproved imports, blocked calls, missing required function."""
    try:
        tree = ast.parse(code)
    except SyntaxError as e:
        return [f"syntax error on line {e.lineno}"]
    flags = []
    defined = {n.name for n in ast.walk(tree) if isinstance(n, (ast.FunctionDef, ast.ClassDef))}
    if fn not in defined:
        flags.append(f"required function '{fn}' is missing")
    for node in ast.walk(tree):
        mods = ([a.name.split(".")[0] for a in node.names] if isinstance(node, ast.Import)
                else [(node.module or "").split(".")[0]] if isinstance(node, ast.ImportFrom) else [])
        flags += [f"unapproved import '{m}'" for m in mods if m not in ALLOWED_IMPORTS]
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id in BLOCKED_CALLS:
            flags.append(f"blocked call '{node.func.id}()'")
    return sorted(set(flags))

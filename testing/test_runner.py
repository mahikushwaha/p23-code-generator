"""Runs the tests in the sandbox and builds a simple summary."""
from sandbox.runner import run_sandboxed
from testing.hidden_tests import build_tests


def run_tests(code, spec):
    tests = build_tests(spec)
    raw = run_sandboxed(code, spec["fn"], tests)
    vis = sum(not t["hidden"] for t in tests)
    out = {"visible_total": vis, "hidden_total": len(tests) - vis, "status": raw["status"],
           "error": raw["error"], "time": raw["time"], "details": [], "failures": []}
    results = {r["id"]: r for r in raw["results"]}
    for t in tests:
        r = results.get(t["id"])
        passed = bool(r and r["passed"])
        d = {"id": t["id"], "hidden": t["hidden"], "expr": t["expr"], "expected": t["expected"],
             "actual": r["actual"] if r else None, "error": r["error"] if r else raw["error"], "passed": passed}
        out["details"].append(d)
        if not passed:
            out["failures"].append(d)
    out["passed"] = len(tests) - len(out["failures"])
    out["failed"] = len(out["failures"])
    out["all_passed"] = out["failed"] == 0
    return out

"""Runs the 15 tasks for real and computes pass@1 and pass-after-retry.
Usage:  python -m evaluation.evaluate [--compare] [--limit N]
"""
import argparse
import csv
import json
import time
from pathlib import Path
from llm.generator import generate_basic
from pipeline import run_pipeline
from testing.test_runner import run_tests
from utils.helpers import load_tasks, task_to_spec

OUT = Path(__file__).resolve().parent
RESULTS_JSON = OUT / "results.json"


def load_results():
    return json.loads(RESULTS_JSON.read_text(encoding="utf-8")) if RESULTS_JSON.exists() else None


def _reason(run):
    if not run["failures"]:
        return run.get("error") or ""
    f = run["failures"][0]
    where = "a hidden test" if f["hidden"] else f"visible test {f['expr']}"
    why = f["error"] or f"wrong output (got {f['actual']!r}, expected {f['expected']!r})"
    return f"Failed {where}: {why}" if not f["hidden"] else f"Failed {where}: {f['error'] or 'wrong output'}"


def run_all(progress=None, compare=False, limit=None):
    tasks = load_tasks()[:limit]
    rows = []
    for i, t in enumerate(tasks):
        spec = task_to_spec(t)
        row = {"task_id": t["id"], "title": t["title"], "category": t["category"], "problem": t["problem"],
               "visible_tests": len(t["visible"]), "hidden_tests": len(t["hidden"])}
        try:
            R = run_pipeline(spec)
            first, ok1 = R["first_run"], R["first_run"]["all_passed"]
            row["first_attempt"] = "PASS" if ok1 else "FAIL"
            row["retry"] = "-" if ok1 else ("PASS" if R["repaired"] else "FAIL")
            row["final"] = "PASS" if R["final_run"]["all_passed"] else "FAIL"
            row["time_s"] = R["time"]
            row["candidates"] = len(R["candidates"])
            row["flagged"] = sum(bool(c["flags"]) for c in R["candidates"])
            row["note"] = "" if ok1 else _reason(first)
        except Exception as e:
            row.update(first_attempt="FAIL", retry="-", final="FAIL", time_s=0, candidates=0, flagged=0, note=f"Pipeline error: {e}")
        if compare:
            try:
                code = generate_basic(t["problem"])
                row["basic_prompt"] = "PASS" if run_tests(code, spec)["all_passed"] else "FAIL"
            except Exception:
                row["basic_prompt"] = "FAIL"
        rows.append(row)
        if progress:
            progress(i + 1, len(tasks), t["title"])
        time.sleep(1)  # be gentle with free-tier rate limits
    n = len(rows)
    p1 = sum(r["first_attempt"] == "PASS" for r in rows)
    fixed = sum(r["first_attempt"] == "FAIL" and r["final"] == "PASS" for r in rows)
    final = sum(r["final"] == "PASS" for r in rows)
    fails = [r for r in rows if r["note"]]
    nc, nf = sum(r["candidates"] for r in rows), sum(r["flagged"] for r in rows)
    summary = {"total": n, "passed_first": p1, "pass_at_1": round(100 * p1 / n, 1), "fixed_after_retry": fixed,
               "final_passed": final, "pass_after_retry": round(100 * final / n, 1),
               "failure_case": (fails[0] if fails else None), "rows": rows,
               "hallucination": {"candidates": nc, "flagged": nf, "rate": round(100 * nf / nc, 1) if nc else 0.0}}
    if compare:
        b = sum(r.get("basic_prompt") == "PASS" for r in rows)
        summary["compare"] = {"basic_pass": b, "basic_pct": round(100 * b / n, 1),
                              "structured_pass": p1, "structured_pct": round(100 * p1 / n, 1)}
    _save(summary)
    return summary


def _save(s):
    RESULTS_JSON.write_text(json.dumps(s, indent=2), encoding="utf-8")
    with open(OUT / "results.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(s["rows"][0].keys()))
        w.writeheader()
        w.writerows(s["rows"])
    md = ["| Metric | Result |", "|---|---:|", f"| Total tasks | {s['total']} |",
          f"| Passed first attempt | {s['passed_first']} |", f"| pass@1 | {s['pass_at_1']}% |",
          f"| Fixed after retry | {s['fixed_after_retry']} |", f"| Final passed | {s['final_passed']} |",
          f"| pass-after-retry | {s['pass_after_retry']}% |", "",
          "| Task | Category | First attempt | Retry | Final | Time (s) |", "|---|---|---|---|---|---:|"]
    md += [f"| {r['task_id']} {r['title']} | {r['category']} | {r['first_attempt']} | {r['retry']} | {r['final']} | {r['time_s']} |"
           for r in s["rows"]]
    h = s["hallucination"]
    md += ["", "| Hallucination check | Result |", "|---|---:|", f"| Solutions generated | {h['candidates']} |",
           f"| Flagged (invented import / blocked call / missing function) | {h['flagged']} |", f"| Flag rate | {h['rate']}% |"]
    if s.get("compare"):
        c = s["compare"]
        md += ["", "| Prompt technique | pass@1 |", "|---|---:|", f"| Basic | {c['basic_pct']}% |",
               f"| Structured | {c['structured_pct']}% |"]
    if s["failure_case"]:
        f = s["failure_case"]
        md += ["", f"**Failure case:** {f['task_id']} {f['title']} - {f['note']}"]
    (OUT / "results.md").write_text("\n".join(md), encoding="utf-8")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--compare", action="store_true", help="also test the basic prompt")
    ap.add_argument("--limit", type=int, default=None)
    a = ap.parse_args()
    s = run_all(progress=lambda i, n, name: print(f"[{i}/{n}] {name}"), compare=a.compare, limit=a.limit)
    print((OUT / "results.md").read_text(encoding="utf-8"))

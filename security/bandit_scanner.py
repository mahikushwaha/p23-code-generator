"""U5 - Bandit security scan of the final code."""
import json
import os
import subprocess
import sys
import tempfile


def scan_code(code):
    counts = {"HIGH": 0, "MEDIUM": 0, "LOW": 0}
    try:
        with tempfile.TemporaryDirectory() as d:
            path = os.path.join(d, "candidate.py")
            open(path, "w", encoding="utf-8").write(code)
            p = subprocess.run([sys.executable, "-m", "bandit", "-f", "json", "-q", path],
                               capture_output=True, text=True, timeout=60)
        data = json.loads(p.stdout)
    except Exception:
        return {"status": "ERROR", "counts": counts, "issues": [],
                "error": "The security scan could not run."}
    issues = []
    for r in data.get("results", []):
        sev = r["issue_severity"].upper()
        counts[sev] = counts.get(sev, 0) + 1
        issues.append({"severity": sev, "text": r["issue_text"], "test_id": r["test_id"],
                       "line": r["line_number"], "snippet": r.get("code", "").strip()})
    status = "PASSED" if counts["HIGH"] == 0 and counts["MEDIUM"] == 0 else "WARNING"
    return {"status": status, "counts": counts, "issues": issues, "error": None}

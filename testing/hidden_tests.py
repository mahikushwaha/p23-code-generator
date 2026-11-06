"""Visible and hidden tests. Hidden ones are kept internally and never displayed with their inputs."""


def build_tests(spec):
    tests = []
    for i, (expr, exp) in enumerate(spec["visible"], 1):
        tests.append({"id": f"V{i}", "hidden": False, "expr": expr, "expected": exp})
    for i, (expr, exp) in enumerate(spec["hidden"], 1):
        tests.append({"id": f"H{i}", "hidden": True, "expr": expr, "expected": exp})
    return tests

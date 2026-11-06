"""The full flow: prompt -> candidates -> CodeBERT rank -> test -> (one repair) -> Bandit."""
import time
from config.settings import NUM_CANDIDATES
from prompting.prompt_builder import basic_prompt, structured_prompt
from llm.generator import generate_candidates, LLMError
from llm.repair import repair_once
from ranking.codebert_ranker import rank_candidates
from testing.test_runner import run_tests
from security.bandit_scanner import scan_code
from sandbox.runner import hallucination_flags

STAGES = ["Generating", "Ranking", "Testing", "Repairing", "Security Scan"]


def run_pipeline(spec, n=NUM_CANDIDATES, repair=True, emit=lambda stage: None):
    t0 = time.time()
    R = {"spec": spec, "basic_prompt": basic_prompt(spec["problem"]), "prompt": structured_prompt(spec),
         "repair_enabled": repair}
    emit("Generating")
    codes = generate_candidates(R["prompt"], n)
    emit("Ranking")
    ranking = rank_candidates(spec["problem"] + "\n" + spec["signature"], codes)
    R["candidates"] = [{"code": c, "flags": hallucination_flags(c, spec["fn"]), **r} for c, r in zip(codes, ranking)]
    best = min(range(len(codes)), key=lambda i: R["candidates"][i]["rank"])
    R["selected"] = best
    emit("Testing")
    first = run_tests(codes[best], spec)
    R.update(first_run=first, final_code=codes[best], final_run=first, repaired=False,
             repair_attempted=False, repair_error=None, repair_skipped=False)
    if not first["all_passed"] and not repair:
        R["repair_skipped"] = True
    if not first["all_passed"] and repair:
        emit("Repairing")
        R["repair_attempted"] = True  # exactly one attempt, no loop
        try:
            fixed = repair_once(spec, codes[best], first)
            second = run_tests(fixed, spec)
            R.update(repaired_code=fixed, repaired_run=second, final_code=fixed, final_run=second,
                     repaired=second["all_passed"])
        except LLMError as e:
            R["repair_error"] = str(e)
    emit("Security Scan")
    R["bandit"] = scan_code(R["final_code"])
    R["time"] = round(time.time() - t0, 1)
    return R

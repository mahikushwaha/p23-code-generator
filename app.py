import streamlit as st
from llm.generator import make_spec, LLMError
from pipeline import run_pipeline, STAGES
from utils.helpers import load_tasks, task_to_spec
from evaluation import evaluate
from media import generate as M
from ui import theme as T
from ui.theme import H, esc, section, banner, tiles, code_block

st.set_page_config(page_title="CodeForge - AI Code Generator with Test Runner", page_icon="⚡", layout="centered")
st.session_state.setdefault("dark", False)
st.session_state.setdefault("page", "Home")
st.session_state.setdefault("problem", "")
T.inject_css(st.session_state.dark)

TASKS = load_tasks()
BY_ID = {t["id"]: t for t in TASKS}
BY_TITLE = {t["title"]: t for t in TASKS}
PAGES = ["Home", "Studio", "Results"]


def go(page):
    st.session_state.page = page


def set_problem(text):
    st.session_state.problem = text
    st.session_state.more = None


def pick_more():
    if st.session_state.get("more"):
        st.session_state.problem = BY_TITLE[st.session_state.more]["problem"]


def get_spec(problem):
    for t in TASKS:  # curated examples have ready-made hidden tests
        if t["problem"].strip() == problem.strip():
            return task_to_spec(t)
    return make_spec(problem)  # custom problem: the AI prepares function name + tests


# ---------------- navigation ----------------
n1, n2, n3 = st.columns([2.2, 6, 1.6], vertical_alignment="center")
n1.markdown('<div class="cf-brand"><div class="cf-logo">⚡</div>CodeForge</div>', unsafe_allow_html=True)
n2.radio("Navigate", PAGES, key="page", horizontal=True, label_visibility="collapsed")
n3.toggle("🌙 Dark", key="dark")
page = st.session_state.page


# ---------------- HOME ----------------
def home():
    H("""<div class="cf-hero"><span class="cf-pill">AI code generator with a built-in test runner</span>
    <h1>Code that is <span>tested</span>, not just written.</h1>
    <p>Describe a Python task. Generate solutions, test them, repair failures, and check the final code before you use it.</p></div>""")
    H('<div class="cf-sp"></div>')
    _, b1, b2, _ = st.columns([2, 1.3, 1.3, 2])
    b1.button("Start Coding", type="primary", use_container_width=True, on_click=go, args=("Studio",))
    b2.button("How It Works", use_container_width=True, on_click=lambda: st.session_state.update(show_how=True))
    steps = [("✏️", "Describe"), ("🧠", "Generate"), ("🏅", "Rank"), ("🧪", "Test"), ("🔧", "Repair"), ("🛡️", "Secure")]
    flow = '<span class="cf-arrow">→</span>'.join(f'<div class="cf-fs">{i} {n}</div>' for i, n in steps)
    H(f'<div class="cf-flow">{flow}</div>')
    if st.session_state.get("show_how"):
        section("How it works", "Six steps, all automatic.")
        how = [("✏️", "Describe", "You write the task in plain English."),
               ("🧠", "Generate", "The AI writes several different solutions."),
               ("🏅", "Rank", "CodeBERT scores how well each solution fits your task."),
               ("🧪", "Test", "The best one runs in a locked sandbox against visible and hidden tests."),
               ("🔧", "Repair", "If a test fails, the error goes back to the AI for one fix."),
               ("🛡️", "Secure", "Bandit scans the final code for security problems.")]
        H('<div class="cf-grid">' + "".join(f'<div class="cf-card"><div class="cf-ico">{i}</div><h4>{t}</h4><p>{d}</p></div>' for i, t, d in how) + "</div>")
    section("Everything between idea and working code", "One workspace, from your description to code you can trust.")
    feats = [("🧠", "AI Code Generation", "Turn plain English into working Python in seconds."),
             ("🗂️", "Multiple Solutions", "Several candidates are written, because the first idea is not always the best."),
             ("🏅", "Smart Ranking", "CodeBERT scores each solution by how well it fits your task."),
             ("🔒", "Hidden Testing", "Visible and hidden tests catch the edge cases you forgot."),
             ("🔧", "Automatic Repair", "If a test fails, the error goes back to the AI for one careful fix."),
             ("🛡️", "Security Scan", "Bandit checks the final code for common security problems.")]
    cards = "".join(f'<div class="cf-card"><div class="cf-ico">{i}</div><h4>{t}</h4><p>{d}</p></div>' for i, t, d in feats)
    H(f'<div class="cf-grid">{cards}</div>')


# ---------------- STUDIO ----------------
def tests_view(run):
    total = run["visible_total"] + run["hidden_total"]
    ok = run["all_passed"]
    tiles([("Passed", f"{run['passed']} / {total}", "tests"), ("Failed", run["failed"], "tests"),
           ("Hidden tests", run["hidden_total"], "inputs kept private"), ("Run time", f"{run['time']} s", "in sandbox")])
    rows, hid = "", [d for d in run["details"] if d["hidden"]]
    for d in run["details"]:
        if d["hidden"]:
            continue
        mark = '<span class="cf-badge ok">PASS</span>' if d["passed"] else '<span class="cf-badge bad">FAIL</span>'
        rows += f'<div class="cf-trow">{mark}<code>{esc(d["expr"])} → {esc(d["expected"])}</code></div>'
    if hid:
        hp = sum(d["passed"] for d in hid)
        mark = '<span class="cf-badge ok">PASS</span>' if hp == len(hid) else '<span class="cf-badge bad">FAIL</span>'
        rows += f'<div class="cf-trow">{mark}<span>🔒 Hidden tests: {hp} / {len(hid)} passed</span></div>'
    H(f'<div class="cf-card">{rows}</div>')
    if run["status"] != "ok":
        failure_card(run["error"])
    elif run["failures"]:
        f = run["failures"][0]
        if f["hidden"]:
            failure_card(f["error"] or "A hidden test returned a wrong answer.", None, None, "A hidden test (inputs stay private)")
        else:
            failure_card(f["error"], f["expected"], f["actual"], f["expr"])
    return ok


def failure_card(error, expected=None, actual=None, test=None):
    extra = ""
    if test:
        extra += f"<div>Test: <code>{esc(test)}</code></div>"
    extra += f"<div>Error: <code>{esc(error or 'wrong answer (no exception)')}</code></div>"
    if expected is not None or actual is not None:
        extra += f"<div>Expected output: <code>{esc(repr(expected))}</code></div><div>Actual output: <code>{esc(repr(actual))}</code></div>"
    H(f'<div class="cf-fail"><b>Test Failed</b>{extra}</div>')


def media_section(R):
    section("Explain, listen & illustrate", "The AI explains the final code in plain English, reads it aloud, and paints an illustration for your task.")
    c1, c2 = st.columns(2)
    if c1.button("🔊 Explain & read aloud", use_container_width=True, key="btn_audio"):
        try:
            with st.spinner("Writing the explanation and recording the voice..."):
                text = M.explain_code(R["spec"]["problem"], R["final_code"])
                st.session_state.media_text, st.session_state.media_audio = text, M.speak(text)
        except LLMError as e:
            banner("bad", "Could not create audio", str(e))
    if c2.button("🖼️ Create illustration", use_container_width=True, key="btn_img"):
        try:
            with st.spinner("Generating the image (can take up to a minute)..."):
                st.session_state.media_img = M.illustration(R["spec"]["problem"])
        except LLMError as e:
            banner("bad", "Could not create the image", str(e))
    if st.session_state.get("media_audio"):
        st.markdown(f"**Explanation:** {esc(st.session_state.media_text)}")
        st.audio(st.session_state.media_audio, format="audio/mp3")
    if st.session_state.get("media_img"):
        st.image(st.session_state.media_img, caption="AI-generated illustration (diffusion model). Check the service's licence before reuse.")
        st.download_button("⬇ Download image", st.session_state.media_img, file_name="illustration.png", mime="image/png")


def render_result(R):
    run, b = R["final_run"], R["bandit"]
    total = run["visible_total"] + run["hidden_total"]
    if run["all_passed"]:
        banner("ok", f"{run['passed']} / {total} tests passed" + (" after automatic repair" if R["repaired"] else ""),
               "Your code is ready." + " Scroll down for the final code.")
    else:
        banner("bad", f"{run['passed']} / {total} tests passed", "Some tests still fail. Review the code carefully before using it.")

    section("Generated Solutions", "CodeBERT scored each solution against your task. The recommended one was tested.")
    for i, c in enumerate(R["candidates"]):
        sel = i == R["selected"]
        score = "n/a" if c["score"] is None else f"{c['score']:.3f}"
        width = 0 if c["score"] is None else int(max(0, min(1, c["score"])) * 100)
        rec = "<span class='cf-badge rec'>Recommended Solution</span>" if sel else ""
        flag = f'<span class="cf-badge bad">Flagged: {esc("; ".join(c["flags"]))}</span>' if c["flags"] else '<span class="cf-badge ok">Guardrail check clean</span>'
        H(f'<div class="cf-sol"><div class="n">Solution {i+1}{rec}'
          f'<span class="cf-badge">Rank #{c["rank"]}</span>{flag}</div>'
          f'<div style="display:flex;align-items:center;gap:.6rem"><span class="cf-muted" style="font-size:.85rem">CodeBERT score</span>'
          f'<div class="cf-bar"><div style="width:{width}%"></div></div><b>{score}</b></div></div>')
        with st.expander(f"View Solution {i+1} code", expanded=sel):
            code_block(c["code"], f"solution_{i+1}.py")
    if any(c["fallback"] for c in R["candidates"]):
        banner("warn", "Ranking unavailable", "CodeBERT could not load, so solutions were used in the order they were written.")

    section("Test Results", "The recommended solution runs in a locked-down sandbox against visible and hidden tests.")
    tests_view(R["first_run"])

    section("Automatic Repair")
    first = R["first_run"]
    if R["repair_attempted"]:
        H('<span class="cf-badge rec" style="margin:0">Repair attempt 1/1</span>')
        if R["repair_error"]:
            banner("bad", "Repair unsuccessful", R["repair_error"])
        else:
            code_block(R["repaired_code"], "repaired_solution.py")
            tests_view(R["repaired_run"])
            if R["repaired"]:
                banner("ok", "Code repaired and tests passed")
            else:
                banner("bad", "Repair unsuccessful", "The corrected code still fails some tests. Only one automatic repair is allowed.")
    elif R["repair_skipped"]:
        banner("warn", "Repair is turned off", "The code failed, but automatic repair was disabled in settings.")
    else:
        banner("info", "No repair needed", "The first solution passed every test.")

    H('<div id="final-result"></div>')
    section("CodeForge Result")
    checks = ["Code generated", "Best solution selected", "Tests completed", "Security scan completed"]
    H('<div class="cf-card">' + "".join(f'<div class="cf-check"><i>✓</i>{c}</div>' for c in checks) + "</div>")
    tiles([("Tests", f"{run['passed']} / {total}", "passed"),
           ("Repair", "Used" if R["repair_attempted"] else "Not needed", "fixed" if R["repaired"] else ("one attempt" if R["repair_attempted"] else "")),
           ("Security", b["status"].title(), f"{sum(b['counts'].values())} finding(s)"),
           ("Total time", f"{R['time']} s", "end to end")])
    code_block(R["final_code"], f"{R['spec']['fn']}.py")
    st.download_button("⬇ Download .py", R["final_code"], file_name=f"{R['spec']['fn']}.py")
    media_section(R)
    with st.expander("Prompts used (basic vs structured)"):
        st.caption("Basic prompt")
        code_block(R["basic_prompt"], "basic_prompt.txt", "text")
        st.caption("Structured prompt (used for generation)")
        code_block(R["prompt"], "structured_prompt.txt", "text")

    section("Security Scan", "Final code checked with Bandit.")
    if b["status"] == "ERROR":
        banner("warn", "Security scan could not run", b["error"])
    else:
        if b["counts"]["HIGH"] == 0:
            banner("ok" if b["status"] == "PASSED" else "warn", "No high-severity security issues detected",
                   "" if b["status"] == "PASSED" else "Medium-severity findings are listed below.")
        else:
            banner("bad", "High-severity security issues detected", "Review them before using this code.")
        tiles([("High", b["counts"]["HIGH"], ""), ("Medium", b["counts"]["MEDIUM"], ""), ("Low", b["counts"]["LOW"], "")])
        for it in b["issues"]:
            with st.expander(f"{it['severity']} · {it['text']} (line {it['line']})"):
                code_block(it["snippet"] or "-", "finding.py", max_h=200)

    section("Licence & originality note", "Please read before you reuse the code.")
    H('''<div class="cf-card"><p>• AI-generated code can resemble existing open-source or copyrighted code. Check it for plagiarism and respect the original licence before you reuse or publish it.
    • The models and tools used here have their own licences (for example CodeBERT is MIT-licensed and Bandit is Apache-2.0). Follow each licence.
    • Review all generated code before using it in production, and never paste passwords or private data into a prompt.</p></div>''')


def studio():
    section("Describe your Python task", "Plain English is fine. Mention edge cases if they matter.")
    ex = [("Palindrome", "T04"), ("Binary search", "T06"), ("GAN generator", "T12"), ("VAE KL loss", "T15")]
    cols = st.columns(4)
    for col, (label, tid) in zip(cols, ex):
        col.button(label, use_container_width=True, key=f"ex_{tid}", on_click=set_problem, args=(BY_ID[tid]["problem"],))
    st.selectbox("More examples", [t["title"] for t in TASKS], index=None, placeholder="More examples...",
                 key="more", on_change=pick_more, label_visibility="collapsed")
    st.text_area("Task", key="problem", height=140, label_visibility="collapsed",
                 placeholder="Write a Python function to check whether a string is a palindrome while ignoring spaces, punctuation and case.")
    s1, s2 = st.columns(2, vertical_alignment="center")
    n = s1.slider("Number of solutions", 2, 4, 3)
    repair = s2.toggle("Repair failed code", value=True)
    if st.button("Generate & Test", type="primary", use_container_width=True):
        problem = st.session_state.problem
        if not problem.strip():
            banner("warn", "Describe a task first", "Type what the code should do, or pick an example above.")
        else:
            ph, state = st.empty(), {"done": [], "active": None}

            def emit(stage):
                if state["active"] and state["active"] != stage:
                    state["done"].append(state["active"])
                state["active"] = stage
                ph.markdown(T.stepper(STAGES, state["done"], stage), unsafe_allow_html=True)

            try:
                emit("Generating")
                spec = get_spec(problem)
                R = run_pipeline(spec, n=n, repair=repair, emit=emit)
                skipped = [] if R["repair_attempted"] else ["Repairing"]
                ph.markdown(T.stepper(STAGES, [s for s in STAGES if s not in skipped], None, skipped), unsafe_allow_html=True)
                st.session_state.R = R
                for k in ("media_text", "media_audio", "media_img"):
                    st.session_state.pop(k, None)
            except LLMError as e:
                ph.empty()
                banner("bad", "Something went wrong", str(e))
            except Exception:
                ph.empty()
                banner("bad", "Something went wrong", "Please try again in a moment.")
    if st.session_state.get("R"):
        render_result(st.session_state.R)
    else:
        H("""<div class="cf-card"><b>Enter a Python problem → Generate code → Test it → Repair it if needed → Check security → Get the final code.</b>
        <p style="margin-top:.4rem">Your results will appear here.</p></div>""")


# ---------------- RESULTS ----------------
def results():
    section("Evaluation dashboard", "15 Python tasks (basic Python, algorithms, data structures, edge cases, PyTorch, GAN and VAE), run end to end.")
    res = evaluate.load_results()
    if res:
        rows = res["rows"]
        avg = sum(r["time_s"] for r in rows) / len(rows)
        tiles([("Tasks tested", res["total"], ""), ("Pass@1", f"{res['pass_at_1']}%", f"{res['passed_first']} passed first try"),
               ("Pass after repair", f"{res['pass_after_retry']}%", f"{res['final_passed']} passed in the end"),
               ("Avg time", f"{avg:.1f} s", "per task"), ("Successful repairs", res["fixed_after_retry"], "fixed by one retry"),
               ("Failed cases", res["total"] - res["final_passed"], "still failing")])
        if res.get("hallucination"):
            h = res["hallucination"]
            section("Hallucination check", "Each generated solution is scanned for invented or unapproved imports, blocked calls and a missing required function.")
            tiles([("Solutions checked", h["candidates"], ""), ("Flagged", h["flagged"], "by the guardrail"), ("Flag rate", f"{h['rate']}%", "lower is better")])
        chip = lambda v: {"PASS": '<span class="cf-badge ok">PASS</span>', "FAIL": '<span class="cf-badge bad">FAIL</span>'}.get(v, "-")
        body = "".join(f"<tr><td>{esc(r['task_id'])}</td><td>{esc(r['title'])}</td><td>{esc(r['category'])}</td><td>{chip(r['first_attempt'])}</td>"
                       f"<td>{chip(r['retry'])}</td><td>{chip(r['final'])}</td><td>{r['time_s']} s</td></tr>" for r in rows)
        H(f'<div class="cf-card cf-scroll"><table class="cf-tbl"><tr><th>ID</th><th>Task</th><th>Category</th><th>First try</th><th>After repair</th><th>Final</th><th>Time</th></tr>{body}</table></div>')
        if res.get("compare"):
            c = res["compare"]
            section("Prompt comparison")
            tiles([("Basic prompt", f"{c['basic_pct']}%", "pass@1"), ("Structured prompt", f"{c['structured_pct']}%", "pass@1")])
        fails = [r for r in rows if r["note"]]
        section("Failure analysis")
        if fails:
            for r in fails[:5]:
                H(f'<div class="cf-fail"><b>{esc(r["task_id"])} · {esc(r["title"])}</b><div>{esc(r["note"])}</div></div>')
        else:
            banner("info", "No failures in the latest run")
    else:
        banner("info", "No results yet", "Run the 15 tasks below. It takes a few minutes and uses AI calls.")
    if st.button("▶ Run the 15-task evaluation", type="primary"):
        bar = st.progress(0.0, text="Starting...")
        evaluate.run_all(progress=lambda i, n, name: bar.progress(i / n, text=f"{i}/{n} · {name}"), compare=True)
        st.rerun()


{"Home": home, "Studio": studio, "Results": results}[page]()
H('<div class="cf-foot">CodeForge · AI-generated code can contain mistakes. Review it before you use it.</div>')

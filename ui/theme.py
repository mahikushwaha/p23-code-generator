"""Look and feel: light/dark CSS, small HTML helpers, dark code viewer with copy button, SVG charts."""
import html
import json
import streamlit as st
import streamlit.components.v1 as components

LIGHT = dict(bg="#f5f7fb", card="#ffffff", text="#0f172a", muted="#64748b", border="#e2e8f0", primary="#2563eb",
             soft="#eff6ff", ok="#15803d", oksoft="#ecfdf3", bad="#dc2626", badsoft="#fef2f2",
             warn="#b45309", warnsoft="#fffbeb", shadow="0 1px 2px rgba(15,23,42,.05),0 8px 24px rgba(15,23,42,.05)")
DARK = dict(bg="#0b1020", card="#131a2e", text="#e6eaf5", muted="#94a3b8", border="#263050", primary="#3b82f6",
            soft="#16264d", ok="#34d399", oksoft="#0f2a22", bad="#f87171", badsoft="#2c1517",
            warn="#fbbf24", warnsoft="#2b2411", shadow="0 1px 2px rgba(0,0,0,.3),0 8px 24px rgba(0,0,0,.25)")

CSS = """
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap');
html,body,.stApp,button,input,textarea{font-family:Inter,system-ui,-apple-system,sans-serif}
.stApp{background:var(--bg);color:var(--text)}
header[data-testid=stHeader],#MainMenu,footer,[data-testid=stSidebar],[data-testid=collapsedControl],[data-testid=stToolbar],[data-testid=stDecoration]{display:none!important}
.block-container{max-width:1080px;padding:1rem 1.2rem 3rem}
[data-testid=stMarkdownContainer] p,[data-testid=stMarkdownContainer] li,[data-testid=stMarkdownContainer] h1,[data-testid=stMarkdownContainer] h2,[data-testid=stMarkdownContainer] h3,[data-testid=stMarkdownContainer] h4{color:var(--text)}
[data-testid=stWidgetLabel] *,[data-testid=stWidgetLabel]{color:var(--text)!important;font-weight:600}
[data-testid=stCaptionContainer],[data-testid=stCaptionContainer] *{color:var(--muted)!important}
.cf-muted{color:var(--muted)!important}
/* nav */
.cf-brand{display:flex;align-items:center;gap:.6rem;font-weight:800;font-size:1.25rem;letter-spacing:-.02em}
.cf-logo{width:34px;height:34px;border-radius:10px;background:var(--primary);color:#fff;display:flex;align-items:center;justify-content:center;font-size:1.1rem}
div[role=radiogroup]{gap:.2rem;flex-wrap:wrap;justify-content:center}
div[role=radiogroup]>label{border-radius:999px;padding:.3rem .95rem;cursor:pointer;margin:0}
div[role=radiogroup]>label>div:first-child{display:none}
div[role=radiogroup]>label:hover{background:var(--soft)}
div[role=radiogroup]>label:has(input:checked){background:var(--primary)}
div[role=radiogroup]>label p{font-weight:600;font-size:.95rem}
div[role=radiogroup]>label:has(input:checked) p{color:#fff!important}
/* inputs */
div[data-baseweb=textarea],div[data-baseweb=textarea] textarea{background:var(--card)!important;color:var(--text)!important;border-radius:14px!important}
div[data-baseweb=textarea]{border:1px solid var(--border)!important;box-shadow:var(--shadow)}
div[data-baseweb=textarea]:focus-within{border-color:var(--primary)!important}
.stTextArea textarea{font-size:1.02rem;line-height:1.55}
div[data-baseweb=select]>div{background:var(--card)!important;border-color:var(--border)!important;border-radius:12px!important}
div[data-baseweb=select] *{color:var(--text)!important}
[data-baseweb=popover]>div,[data-baseweb=popover] ul,[data-baseweb=popover] li{background:var(--card)!important;color:var(--text)!important}
[data-testid=stSliderThumbValue],[data-testid=stTickBarMin],[data-testid=stTickBarMax]{color:var(--text)!important}
/* buttons */
.stButton>button,.stDownloadButton>button{border-radius:12px;border:1px solid var(--border);background:var(--card);color:var(--text);font-weight:600;padding:.55rem 1rem;box-shadow:var(--shadow);transition:all .15s}
.stButton>button:hover,.stDownloadButton>button:hover{border-color:var(--primary);color:var(--primary)}
.stButton>button p,.stDownloadButton>button p{color:inherit!important}
.stButton>button[kind=primary]{background:var(--primary);border-color:var(--primary);color:#fff}
.stButton>button[kind=primary]:hover{filter:brightness(1.08);color:#fff}
.stButton>button[kind=primary] p{color:#fff!important}
[data-testid=stExpander]{background:var(--card);border:1px solid var(--border)!important;border-radius:14px;box-shadow:var(--shadow)}
[data-testid=stExpander] summary,[data-testid=stExpander] summary *{color:var(--text)!important;font-weight:600}
.stTabs [data-baseweb=tab]{color:var(--muted)!important;font-weight:600}
.stTabs [aria-selected=true]{color:var(--primary)!important}
.stTabs [data-baseweb=tab-border]{background:var(--border)}
.stTabs [data-baseweb=tab-highlight]{background:var(--primary)}
/* components */
.cf-hero{text-align:center;padding:64px 20px 36px;border:1px solid var(--border);border-radius:24px;background:radial-gradient(ellipse at 50% 0%,var(--soft),var(--card) 70%);box-shadow:var(--shadow)}
.cf-pill{display:inline-block;padding:.25rem .8rem;border-radius:999px;background:var(--soft);color:var(--primary);font-weight:600;font-size:.82rem;margin-bottom:1rem}
.cf-hero h1{font-size:clamp(2rem,5.5vw,3.4rem);font-weight:800;letter-spacing:-.03em;line-height:1.1;margin:0 0 1rem;padding:0}
.cf-hero h1 span{color:var(--primary)}
.cf-hero p{max-width:640px;margin:0 auto;font-size:1.08rem;line-height:1.6;color:var(--muted)!important}
.cf-h2{font-size:1.45rem;font-weight:700;letter-spacing:-.02em;margin:2rem 0 .2rem}
.cf-sub{color:var(--muted)!important;margin:0 0 1rem;line-height:1.5}
.cf-flow{display:flex;flex-wrap:wrap;gap:.6rem;align-items:center;justify-content:center;margin:1.4rem 0}
.cf-fs{display:flex;align-items:center;gap:.5rem;padding:.65rem 1rem;border-radius:14px;border:1px solid var(--border);background:var(--card);font-weight:600;box-shadow:var(--shadow)}
.cf-arrow{color:var(--muted);font-weight:700}
.cf-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(250px,1fr));gap:1rem;margin:1rem 0}
.cf-card{border:1px solid var(--border);background:var(--card);border-radius:18px;padding:1.2rem 1.3rem;box-shadow:var(--shadow);margin:.5rem 0}
.cf-card h4{margin:.6rem 0 .3rem;font-size:1.05rem;font-weight:700}
.cf-card p{margin:0;color:var(--muted)!important;line-height:1.55;font-size:.94rem}
.cf-ico{width:42px;height:42px;border-radius:12px;background:var(--soft);display:flex;align-items:center;justify-content:center;font-size:1.3rem}
.cf-tiles{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:.8rem;margin:.6rem 0 1rem}
.cf-tile{border:1px solid var(--border);background:var(--card);border-radius:16px;padding:.9rem 1.1rem;box-shadow:var(--shadow)}
.cf-tile .l{font-size:.8rem;color:var(--muted)!important;font-weight:600;text-transform:uppercase;letter-spacing:.04em}
.cf-tile .v{font-size:1.65rem;font-weight:800;letter-spacing:-.02em;margin-top:.15rem}
.cf-tile .s{font-size:.8rem;color:var(--muted)!important}
.cf-banner{display:flex;gap:.8rem;align-items:flex-start;padding:1rem 1.2rem;border-radius:16px;border:1px solid;margin:.6rem 0}
.cf-banner b{display:block;font-size:1.05rem}
.cf-banner span.t{color:inherit;opacity:.9;font-size:.92rem}
.cf-banner.ok{background:var(--oksoft);border-color:var(--ok);color:var(--ok)}
.cf-banner.bad{background:var(--badsoft);border-color:var(--bad);color:var(--bad)}
.cf-banner.warn{background:var(--warnsoft);border-color:var(--warn);color:var(--warn)}
.cf-banner.info{background:var(--soft);border-color:var(--primary);color:var(--primary)}
.cf-prog{display:flex;flex-wrap:wrap;gap:.5rem;margin:.8rem 0}
.cf-ps{display:flex;align-items:center;gap:.45rem;padding:.45rem .9rem;border-radius:999px;border:1px solid var(--border);background:var(--card);font-weight:600;font-size:.88rem;color:var(--muted)}
.cf-ps.done{color:var(--ok);border-color:var(--ok);background:var(--oksoft)}
.cf-ps.active{color:var(--primary);border-color:var(--primary);background:var(--soft)}
.cf-ps.skip{border-style:dashed;opacity:.7}
.cf-dot{width:8px;height:8px;border-radius:50%;background:currentColor}
.active .cf-dot{animation:cfp 1s ease-in-out infinite}
@keyframes cfp{50%{opacity:.25}}
.cf-sol{display:flex;flex-wrap:wrap;justify-content:space-between;align-items:center;gap:.6rem;padding:.2rem 0 .6rem}
.cf-sol .n{font-weight:700;font-size:1.05rem}
.cf-badge{display:inline-block;padding:.18rem .65rem;border-radius:999px;font-size:.78rem;font-weight:700;background:var(--soft);color:var(--primary)!important;margin-left:.4rem}
.cf-badge.rec{background:var(--primary);color:#fff!important}
.cf-badge.ok{background:var(--oksoft);color:var(--ok)!important}
.cf-badge.bad{background:var(--badsoft);color:var(--bad)!important}
.cf-bar{height:8px;border-radius:99px;background:var(--border);overflow:hidden;min-width:120px}
.cf-bar>div{height:100%;background:var(--primary);border-radius:99px}
.cf-trow{display:flex;gap:.7rem;align-items:flex-start;padding:.55rem .2rem;border-bottom:1px solid var(--border)}
.cf-trow code{font-family:'JetBrains Mono',monospace;font-size:.85rem;word-break:break-all}
.cf-fail{border:1px solid var(--bad);background:var(--badsoft);border-radius:14px;padding:.9rem 1.1rem;margin:.6rem 0}
.cf-fail b{color:var(--bad)}
.cf-fail div{margin-top:.3rem;font-size:.9rem}
.cf-fail code{font-family:'JetBrains Mono',monospace;font-size:.85rem}
.cf-check{padding:.2rem 0;font-weight:600}
.cf-check i{font-style:normal;color:var(--ok);margin-right:.5rem}
.cf-tbl{width:100%;border-collapse:collapse;font-size:.92rem}
.cf-tbl th{text-align:left;font-size:.78rem;text-transform:uppercase;letter-spacing:.04em;color:var(--muted);padding:.6rem .7rem;border-bottom:1px solid var(--border)}
.cf-tbl td{padding:.6rem .7rem;border-bottom:1px solid var(--border)}
.cf-scroll{overflow-x:auto}
.cf-prob{display:flex;align-items:center;gap:.7rem;margin:.35rem 0}
.cf-prob .k{width:70px;font-family:'JetBrains Mono',monospace;font-size:.85rem}
.cf-prob .b{flex:1;height:18px;background:var(--border);border-radius:6px;overflow:hidden}
.cf-prob .b>div{height:100%;background:var(--primary);border-radius:6px;transition:width .25s}
.cf-prob .p{width:52px;text-align:right;font-weight:600;font-size:.85rem}
.cf-foot{text-align:center;color:var(--muted)!important;font-size:.85rem;margin-top:3rem}
.cf-sp{height:.6rem}
"""


def inject_css(dark):
    v = DARK if dark else LIGHT
    root = ":root{" + "".join(f"--{k}:{x};" for k, x in v.items()) + "}"
    st.markdown(f"<style>{root}{CSS}</style>", unsafe_allow_html=True)


def H(s):
    """Render HTML (strip indentation/blank lines so Markdown doesn't treat it as code)."""
    st.markdown("\n".join(l.strip() for l in s.splitlines() if l.strip()), unsafe_allow_html=True)


def esc(x):
    return html.escape(str(x))


def section(title, sub=""):
    H(f'<div class="cf-h2">{esc(title)}</div>' + (f'<p class="cf-sub">{sub}</p>' if sub else ""))


def banner(kind, title, text=""):
    icon = {"ok": "✓", "bad": "✕", "warn": "!", "info": "i"}[kind]
    H(f'<div class="cf-banner {kind}"><b style="font-size:1.3rem">{icon}</b><div><b>{esc(title)}</b>'
      f'<span class="t">{esc(text)}</span></div></div>')


def tiles(items):
    cells = "".join(f'<div class="cf-tile"><div class="l">{esc(l)}</div><div class="v">{esc(v)}</div>'
                    f'<div class="s">{esc(s)}</div></div>' for l, v, s in items)
    H(f'<div class="cf-tiles">{cells}</div>')


def stepper(stages, done, active, skipped=()):
    out = ""
    for s in stages:
        cls = "done" if s in done else "active" if s == active else "skip" if s in skipped else ""
        mark = "✓" if cls == "done" else '<span class="cf-dot"></span>'
        out += f'<div class="cf-ps {cls}">{mark} {s}</div>'
    return f'<div class="cf-prog">{out}</div>'


CODE_HTML = """<!doctype html><html><head><meta charset="utf-8"><style>
html,body{margin:0;height:100%;background:transparent;font-family:Inter,system-ui,sans-serif}
.box{height:100%;display:flex;flex-direction:column;background:#0d1117;border:1px solid #263050;border-radius:14px;overflow:hidden}
.bar{display:flex;align-items:center;justify-content:space-between;padding:8px 12px;background:#161b22;border-bottom:1px solid #263050}
.dots span{display:inline-block;width:10px;height:10px;border-radius:50%;margin-right:6px}
.name{color:#8b949e;font-size:12px;font-family:'JetBrains Mono',monospace}
button{background:#2563eb;color:#fff;border:0;border-radius:8px;padding:5px 12px;font-weight:600;font-size:12px;cursor:pointer}
button:hover{filter:brightness(1.1)}
pre{margin:0;padding:14px 16px;overflow:auto;flex:1;color:#e6edf3;font:13px/1.55 'JetBrains Mono',ui-monospace,Consolas,monospace}
.k{color:#ff7b72}.s{color:#a5d6ff}.c{color:#8b949e;font-style:italic}.n{color:#79c0ff}
</style></head><body><div class="box"><div class="bar"><div class="dots"><span style="background:#ff5f56"></span><span style="background:#ffbd2e"></span><span style="background:#27c93f"></span></div>
<span class="name">__NAME__</span><button id="cp">Copy</button></div><pre id="code"></pre></div>
<script>
const code=__CODE__, lang="__LANG__";
const esc=s=>s.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');
let out;
if(lang==="python"){
 const re=/(#[^\\n]*)|(\"\"\"[\\s\\S]*?\"\"\"|'''[\\s\\S]*?'''|\"(?:\\\\.|[^\"\\\\\\n])*\"|'(?:\\\\.|[^'\\\\\\n])*')|\\b(def|class|return|if|elif|else|for|while|in|not|and|or|import|from|as|with|try|except|finally|raise|lambda|None|True|False|pass|break|continue|yield|is|self)\\b|\\b(\\d+\\.?\\d*)\\b/g;
 out='';let last=0,m;
 while((m=re.exec(code))){out+=esc(code.slice(last,m.index));const c=m[1]?'c':m[2]?'s':m[3]?'k':'n';out+='<span class="'+c+'">'+esc(m[0])+'</span>';last=re.lastIndex;}
 out+=esc(code.slice(last));
}else{out=esc(code);}
document.getElementById('code').innerHTML=out;
document.getElementById('cp').onclick=function(){
 const b=this;const ta=document.createElement('textarea');ta.value=code;document.body.appendChild(ta);ta.select();
 try{document.execCommand('copy')}catch(e){}ta.remove();
 if(navigator.clipboard){navigator.clipboard.writeText(code).catch(()=>{})}
 b.textContent='Copied ✓';setTimeout(()=>b.textContent='Copy',1500);};
</script></body></html>"""


def code_block(code, name="solution.py", lang="python", max_h=460):
    lines = code.count("\n") + 1
    height = int(min(max_h, 64 + lines * 20.5))
    page = (CODE_HTML.replace("__NAME__", esc(name)).replace("__LANG__", lang)
            .replace("__CODE__", json.dumps(code).replace("</", "<\\/")))
    components.html(page, height=height, scrolling=False)


PALETTE = ["#2563eb", "#f59e0b", "#10b981", "#ec4899"]


def svg_scatter(points, names):
    """points: list of (x, y, class_index). Theme-aware SVG scatter plot."""
    xs, ys = [p[0] for p in points], [p[1] for p in points]
    x0, x1, y0, y1 = min(xs), max(xs), min(ys), max(ys)
    W, Hh, pad = 600, 340, 34
    sx = lambda x: pad + (x - x0) / ((x1 - x0) or 1) * (W - 2 * pad)
    sy = lambda y: Hh - pad - (y - y0) / ((y1 - y0) or 1) * (Hh - 2 * pad)
    dots = "".join(f'<circle cx="{sx(x):.1f}" cy="{sy(y):.1f}" r="4" fill="{PALETTE[c % 4]}" fill-opacity=".7"/>'
                   for x, y, c in points)
    axes = (f'<line x1="{pad}" y1="{Hh-pad}" x2="{W-pad}" y2="{Hh-pad}" style="stroke:var(--border)"/>'
            f'<line x1="{pad}" y1="{pad}" x2="{pad}" y2="{Hh-pad}" style="stroke:var(--border)"/>'
            f'<text x="{W/2}" y="{Hh-8}" text-anchor="middle" font-size="12" style="fill:var(--muted)">latent dimension 1</text>'
            f'<text x="12" y="{Hh/2}" font-size="12" style="fill:var(--muted)" transform="rotate(-90 12 {Hh/2})" text-anchor="middle">latent dimension 2</text>')
    legend = "".join(f'<span style="margin-right:1rem;font-size:.85rem"><span style="display:inline-block;width:10px;height:10px;'
                     f'border-radius:50%;background:{PALETTE[i]};margin-right:.35rem"></span>{esc(n)}</span>'
                     for i, n in enumerate(names))
    H(f'<div class="cf-card"><svg viewBox="0 0 {W} {Hh}" style="width:100%;height:auto">{axes}{dots}</svg>'
      f'<div style="margin-top:.5rem">{legend}</div></div>')

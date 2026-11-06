---
title: CodeForge
colorFrom: blue
colorTo: indigo
sdk: docker
app_port: 8501
pinned: false
---

# CodeForge â€“ P23 Code Generator with Test Runner (Roll No. 23)

## 1. Problem statement
Generate Python from a plain-English task, test it, and repair it once on failure.

## 2. Features
Plain-English input Â· 3 candidate solutions Â· CodeBERT ranking Â· sandboxed visible + hidden tests Â· exactly one auto-repair Â· Bandit scan Â· download code Â· built-in 15-task evaluation Â· works on phone and desktop.

## 3. Architecture
Problem â†’ U1 structured prompt â†’ U2 LLM (3 candidates) â†’ U3 CodeBERT rank â†’ U4 sandbox tests â†’ pass? â†’ (no: one LLM repair â†’ re-test) â†’ U5 Bandit â†’ final output. The same diagram is in the app's **How it works** tab.

## 4. U1â€“U5 implementation
| Unit | File | What it does |
|---|---|---|
| U1 | `prompting/prompt_builder.py` | Basic vs structured prompt (spec, I/O, examples, constraints, function name, safety) |
| U2 | `llm/generator.py`, `llm/repair.py` | Candidate generation; one repair with error + failed test + expected/actual |
| U3 | `ranking/codebert_ranker.py` | `microsoft/codebert-base` embeddings, cosine similarity, ranking |
| U4 | `sandbox/runner.py`, `testing/` | AST check, subprocess, temp dir, clean env, CPU/RAM/file limits, timeout, no network; visible + hidden tests; GAN/VAE tasks in `evaluation/tasks.json` |
| U5 | `security/bandit_scanner.py`, `model_card.md` | Bandit scan, licence/IP and safety notes, model card |

## 5. Technology stack
Python 3.10+, Streamlit, PyTorch, Hugging Face Transformers (CodeBERT), Bandit, Groq or Gemini API (REST), Git/GitHub, Hugging Face Spaces.

## 6. Installation and local run
```bash
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```
## 7. Secrets (never commit keys)
Local: `export GROQ_API_KEY="your-key"` (Windows PowerShell: `$env:GROQ_API_KEY="your-key"`) or copy `.streamlit/secrets.toml.example` to `.streamlit/secrets.toml`.
To use Gemini: `LLM_PROVIDER=gemini` and `GEMINI_API_KEY=...`. Free keys: console.groq.com or aistudio.google.com.
```bash
streamlit run app.py
```

## 8. Deploy (Hugging Face Spaces â€“ recommended)
1. Create a Space at huggingface.co/new-space â†’ SDK **Streamlit** â†’ Public.
2. Push this repo to the Space (or connect it to GitHub).
3. Space â†’ Settings â†’ **Variables and secrets** â†’ add `GROQ_API_KEY` (and `LLM_PROVIDER` if not groq).
4. Wait for the build; your URL is `https://huggingface.co/spaces/<user>/<space>`.
Streamlit Community Cloud also works, but its 1 GB RAM can be too small for PyTorch + CodeBERT.

## 9. Evaluation methodology
`python -m evaluation.evaluate --compare` runs the 15 tasks (basic Python, algorithms, data structures, edge cases, PyTorch, 2 GAN, 2 VAE). For each task: generate 3 candidates â†’ CodeBERT picks one â†’ run visible + hidden tests (**first attempt**) â†’ if it fails, one repair and re-test (**retry**).
- **pass@1** = tasks passing on the first selected solution Ã· 15 Ã— 100
- **pass-after-retry** = tasks passing after the single allowed repair Ã· 15 Ã— 100
- `--compare` also measures the basic prompt (prompt-technique comparison).
- **Hallucination check:** every generated solution is scanned for invented/unapproved imports, blocked calls and a missing required function; the flag rate is reported (measured test for Responsible AI).
Outputs: `evaluation/results.json`, `results.csv`, `results.md`. Nothing is hard-coded.

## 10. Results
Run the command above and paste `evaluation/results.md` here:

| Metric | Result |
|---|---:|
| Total tasks | 15 |
| pass@1 | _fill after run_ |
| pass-after-retry | _fill after run_ |

**Failure case:** _copy the failure case printed by the run and explain the cause._

## 11. Security
Generated code is checked (allowed imports only, no eval/exec/open), run in a separate process with a timeout, temp folder, minimal environment, memory/CPU limits and network disabled, then scanned with Bandit. The sandbox reduces risk but does not guarantee security.

## 12. Ethical considerations
LLM code can be buggy or insecure, may resemble copyrighted code, and must be reviewed before production. Respect licences of models and libraries. User text is sent to the LLM provider.

## 13. Licence
MIT for this project code. CodeBERT: MIT. Check the licence of the LLM you use.

## Media features (image + audio)
In Studio, after the code is final: **Explain & read aloud** (LLM explanation + gTTS text-to-speech) and **Create illustration** (diffusion model via the free Pollinations service, with an optional Hugging Face FLUX backup if you add an `HF_TOKEN` secret). Generated images are labelled AI-generated; check the image service's licence before reuse.


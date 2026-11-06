"""Central settings. Keys come from environment variables or Streamlit secrets - never from code."""
import os

CODEBERT_MODEL = "microsoft/codebert-base"
NUM_CANDIDATES = 3
MAX_REPAIR_ATTEMPTS = 1  # exactly one automatic repair

# Imports the generated code may use (checked before running, also told to the LLM)
ALLOWED_IMPORTS = {
    "math", "itertools", "collections", "re", "heapq", "functools", "string", "typing",
    "json", "random", "bisect", "statistics", "decimal", "fractions", "operator",
    "copy", "dataclasses", "numpy", "torch",
}
BLOCKED_CALLS = {"eval", "exec", "open", "compile", "__import__", "input", "breakpoint"}


def secret(name, default=None):
    value = os.environ.get(name)
    if value:
        return value
    try:
        import streamlit as st
        return st.secrets.get(name, default)
    except Exception:
        return default


def provider():
    return str(secret("LLM_PROVIDER", "groq")).lower()


def api_key():
    return secret("GEMINI_API_KEY") if provider() == "gemini" else secret("GROQ_API_KEY")


def model_name():
    if provider() == "gemini":
        return secret("GEMINI_MODEL", "gemini-2.5-flash")
    return secret("GROQ_MODEL", "llama-3.3-70b-versatile")

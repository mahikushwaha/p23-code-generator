"""Audio + image generation for Studio: spoken explanation (TTS) and a diffusion illustration."""
import io
import urllib.parse
import requests
from config.settings import secret
from llm.generator import call_llm, LLMError


def explain_code(problem, code):
    prompt = ("Explain this Python code to a beginner in 3 short sentences (max 60 words). "
              f"No code and no markdown.\nTask: {problem}\n```python\n{code}\n```")
    return call_llm(prompt, temperature=0.3).strip()


def speak(text):
    """Text-to-speech (gTTS) -> MP3 bytes."""
    try:
        from gtts import gTTS
        buf = io.BytesIO()
        gTTS(text=text, lang="en").write_to_fp(buf)
        return buf.getvalue()
    except Exception:
        raise LLMError("Voice is unavailable right now. It needs an internet connection.")


def _is_image(r):
    return r.status_code == 200 and r.headers.get("content-type", "").startswith("image")


def illustration(problem):
    """Diffusion-model illustration for the task. Free Pollinations service first, Hugging Face as backup."""
    prompt = ("Minimal flat vector illustration, blue and white colour palette, no text, "
              f"concept art for a Python programming task: {problem[:160]}")
    try:
        url = "https://image.pollinations.ai/prompt/" + urllib.parse.quote(prompt) + "?width=768&height=512&nologo=true"
        r = requests.get(url, timeout=90)
        if _is_image(r):
            return r.content
    except requests.RequestException:
        pass
    token = secret("HF_TOKEN")
    if token:
        try:
            r = requests.post("https://router.huggingface.co/hf-inference/models/black-forest-labs/FLUX.1-schnell",
                              headers={"Authorization": f"Bearer {token}"}, json={"inputs": prompt}, timeout=120)
            if _is_image(r):
                return r.content
        except requests.RequestException:
            pass
    raise LLMError("The image service is busy or unreachable. Please try again in a moment.")

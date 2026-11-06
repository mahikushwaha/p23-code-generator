"""U3 - rank candidates with CodeBERT: cosine similarity between problem and code embeddings."""
from config.settings import CODEBERT_MODEL

_tok = _model = None


def _load():
    global _tok, _model
    if _model is None:
        from transformers import AutoTokenizer, AutoModel
        _tok = AutoTokenizer.from_pretrained(CODEBERT_MODEL)
        _model = AutoModel.from_pretrained(CODEBERT_MODEL).eval()


def _embed(texts):
    import torch
    import torch.nn.functional as F
    inputs = _tok(texts, padding=True, truncation=True, max_length=256, return_tensors="pt")
    with torch.no_grad():
        hidden = _model(**inputs).last_hidden_state
    mask = inputs["attention_mask"].unsqueeze(-1)
    pooled = (hidden * mask).sum(1) / mask.sum(1)  # mean pooling
    return F.normalize(pooled, dim=1)


def rank_candidates(problem, codes):
    """Returns [{'score': float|None, 'rank': int}] in the same order as codes."""
    try:
        _load()
        vecs = _embed([problem] + codes)
        scores = (vecs[1:] @ vecs[0]).tolist()
        order = sorted(range(len(codes)), key=lambda i: -scores[i])
        ranks = {i: r + 1 for r, i in enumerate(order)}
        return [{"score": round(scores[i], 4), "rank": ranks[i], "fallback": False} for i in range(len(codes))]
    except Exception:
        # CodeBERT unavailable: keep original order so the app still works
        return [{"score": None, "rank": i + 1, "fallback": True} for i in range(len(codes))]

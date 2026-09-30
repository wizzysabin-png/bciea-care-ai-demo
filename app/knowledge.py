from pathlib import Path
import re
from typing import List, Dict

KNOWLEDGE_DIR = Path(__file__).resolve().parent / "knowledge"


def _load_docs() -> List[Dict[str, str]]:
    docs = []
    for path in KNOWLEDGE_DIR.glob("*.md"):
        text = path.read_text(encoding="utf-8")
        title = text.splitlines()[0].lstrip("# ").strip() if text else path.stem
        docs.append({"title": title, "text": text})
    return docs

DOCS = _load_docs()


def retrieve(query: str, k: int = 3) -> List[Dict[str, str]]:
    terms = {w for w in re.findall(r"[a-zA-ZÀ-ÿ']+", query.lower()) if len(w) > 2}
    scored = []
    for doc in DOCS:
        body = doc["text"].lower()
        score = sum(body.count(t) for t in terms)
        if score:
            scored.append((score, doc))
    scored.sort(key=lambda x: x[0], reverse=True)
    return [doc for _, doc in scored[:k]] or DOCS[:2]

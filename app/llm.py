from typing import List, Dict, Optional
import httpx
from .config import LLM_MODE, OLLAMA_URL, OLLAMA_MODEL

SYSTEM_PROMPT = """You are BCIEA Care AI, a breast-health education and patient-navigation assistant.
Safety rules:
- Never diagnose or rule out cancer.
- Never prescribe, change, or stop medication.
- Never fabricate test results, appointments, clinicians, or facilities.
- Encourage qualified clinical assessment when the safety engine indicates it.
- Use simple, compassionate language.
- Respond in the user's selected language when possible.
- If uncertain, say so and recommend human help.
"""

async def draft_with_llm(user_message: str, language: str, triage_level: str, knowledge: List[Dict[str, str]]) -> Optional[str]:
    if LLM_MODE != "ollama":
        return None
    context = "\n\n".join(d["text"][:2500] for d in knowledge)
    prompt = f"""Language: {language}\nTriage level: {triage_level}\nApproved knowledge:\n{context}\n\nUser: {user_message}\n\nWrite a safe response. Do not override the triage level."""
    try:
        async with httpx.AsyncClient(timeout=25) as client:
            r = await client.post(f"{OLLAMA_URL}/api/chat", json={
                "model": OLLAMA_MODEL,
                "stream": False,
                "messages": [
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": prompt},
                ],
            })
            r.raise_for_status()
            return r.json().get("message", {}).get("content")
    except Exception:
        return None

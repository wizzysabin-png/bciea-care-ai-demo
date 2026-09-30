from .triage import triage_text
from .knowledge import retrieve
from .llm import draft_with_llm

FOLLOWUPS_EN = {
    "needs_assessment": "If you are comfortable sharing: when did you first notice it, has it changed, is there pain, discharge, skin change, fever, or a lump in the armpit? I can also help create a referral request.",
    "urgent": "Please prioritize contacting a health professional or facility. If symptoms become severe or you feel very unwell, seek emergency care.",
    "emergency": "Please stop using the chat for now and seek emergency medical help.",
    "education": "You can ask me about breast awareness, screening, symptoms, referrals, preparing for an appointment, or BCIEA support.",
}
FOLLOWUPS_RW = {
    "needs_assessment": "Niba wumva wabimbwira: wabibonye ryari bwa mbere, byarahindutse, birababaza, hari amazi cyangwa amaraso ava mu ibere, impinduka ku ruhu, umuriro, cyangwa akabyimba mu kwaha? Nshobora no kugufasha gukora ubusabe bwo koherezwa kwa muganga.",
    "urgent": "Gerageza kuvugana n'umuganga cyangwa ikigo nderabuzima byihutirwa. Niba ibimenyetso bikabije cyangwa ukumva urarembye cyane, shaka ubutabazi bwihuse.",
    "emergency": "Hagarika gukoresha iki kiganiro ubu maze ushake ubutabazi bwihuse bw'abaganga.",
    "education": "Ushobora kumbaza ku kwimenya amabere, kwisuzumisha, ibimenyetso, koherezwa kwa muganga, kwitegura kujya kwa muganga, cyangwa ubufasha bwa BCIEA.",
}

async def respond(message: str, language: str = "rw"):
    triage = triage_text(message)
    docs = retrieve(message)
    llm_text = await draft_with_llm(message, language, triage.level, docs)
    if llm_text:
        response = llm_text.strip()
    else:
        safety = triage.safety_message_rw if language.startswith("rw") else triage.safety_message_en
        follow = FOLLOWUPS_RW[triage.level] if language.startswith("rw") else FOLLOWUPS_EN[triage.level]
        response = f"{safety}\n\n{follow}"
    rw = language.startswith("rw")
    return {
        "response": response,
        "risk_score": triage.score,
        "signals": triage.matched,
        "barriers": triage.barriers,
        "timeframe": triage.timeframe_rw if rw else triage.timeframe_en,
        "plan": triage.plan_rw if rw else triage.plan_en,
        "triage_level": triage.level,
        "knowledge_titles": [d["title"] for d in docs],
        "human_handoff_recommended": triage.level in {"emergency", "urgent", "needs_assessment"},
    }

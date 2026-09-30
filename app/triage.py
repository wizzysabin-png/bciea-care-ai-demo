import re
from dataclasses import dataclass
from typing import List


@dataclass
class TriageResult:
    level: str
    matched: List[str]
    safety_message_en: str
    safety_message_rw: str


RULES = {
    "emergency": [
        r"trouble breathing|difficulty breathing|can't breathe|cannot breathe|fainting|unconscious|severe bleeding|collapse",
        r"kubura umwuka|guhumeka bigoye|yaguye igihumure|nta ubwenge|kuva amaraso menshi",
    ],
    "urgent": [
        r"breast.*red.*fever|redness.*fever|high fever.*breast|severe breast pain.*fever|rapidly worsening",
        r"ibere.*ritukura.*umuriro|umuriro.*ibere|ububabare bukabije.*umuriro|birimo kwiyongera vuba",
    ],
    "needs_assessment": [
        r"lump|mass|nipple discharge|bloody discharge|dimpling|orange peel|skin change|nipple inversion|new breast change|underarm lump",
        r"akabyimba|ikibyimba|amazi ava mu ibere|amaraso ava mu ibere|uruhu rw'ibere|uruhu rumeze nk'icunga|imoko yibere yinjiye|impinduka mu ibere|akabyimba mu kwaha",
    ],
}


def triage_text(text: str) -> TriageResult:
    t = text.lower().strip()
    for level in ("emergency", "urgent", "needs_assessment"):
        matched = [p for p in RULES[level] if re.search(p, t, flags=re.I)]
        if matched:
            if level == "emergency":
                return TriageResult(level, matched,
                    "Your message may describe an emergency. Please seek urgent in-person medical help now or contact local emergency services. Do not wait for this chat.",
                    "Ubutumwa bwawe bushobora kugaragaza ikibazo cyihutirwa cyane. Shaka ubufasha bw'abaganga ako kanya cyangwa uhamagare serivisi z'ubutabazi. Ntutegereze iki kiganiro.")
            if level == "urgent":
                return TriageResult(level, matched,
                    "This may need urgent medical assessment today, especially if symptoms are worsening or you have fever. Please contact a health professional or facility promptly.",
                    "Ibi bishobora gusaba ko usuzumwa n'umuganga byihutirwa uyu munsi, cyane cyane niba birushaho kwiyongera cyangwa ufite umuriro. Vugana n'umuganga cyangwa ikigo nderabuzima vuba.")
            return TriageResult(level, matched,
                "This breast change should be assessed by a qualified health professional. It does not automatically mean cancer, but it should not be ignored.",
                "Iyi mpinduka yo mu ibere ikwiye gusuzumwa n'umuganga ubifitiye ubushobozi. Ntibivuze ko ari kanseri byanze bikunze, ariko ntikwiye kwirengagizwa.")
    return TriageResult("education", [],
        "I can provide breast-health education and help you decide the appropriate next step, but I cannot diagnose cancer.",
        "Nshobora gutanga amakuru ku buzima bw'amabere no kugufasha kumenya intambwe ikwiye gukurikira, ariko sinshobora gusuzuma kanseri.")

"""BCIEA risk-scoring triage.
Hard safety rules (emergency/urgent regex) ALWAYS win; weighted scoring can only ESCALATE, never downgrade.
All weights/thresholds are placeholders: BCIEA clinicians must review before real use."""
import re
from dataclasses import dataclass, field
from typing import List

NEG = r"(?<!no )(?<!not )(?<!without )(?<!nta )"  # simple negation guard: "no lump" is ignored
EMERGENCY = r"trouble breathing|difficulty breathing|can't breathe|cannot breathe|fainting|unconscious|severe bleeding|collapse|kubura umwuka|guhumeka bigoye|yaguye igihumure|nta ubwenge|kuva amaraso menshi"
URGENT = r"breast.*red.*fever|redness.*fever|high fever.*breast|severe breast pain.*fever|rapidly worsening|ibere.*ritukura.*umuriro|umuriro.*ibere|ububabare bukabije.*umuriro|birimo kwiyongera vuba"
SIGNALS = [  # (label, pattern, weight)
    ("Breast lump", r"\blump|\bmass\b|akabyimba|ikibyimba", 30),
    ("Underarm lump", r"underarm|armpit|kwaha", 20),
    ("Bloody nipple discharge", r"bloody discharge|blood.*nipple|amaraso ava mu ibere", 30),
    ("Nipple discharge", r"nipple discharge|amazi ava mu ibere", 20),
    ("Skin change", r"dimpl|orange peel|skin change|uruhu", 20),
    ("Nipple change", r"nipple inversion|inverted nipple|imoko yibere yinjiye", 18),
    ("New breast change", r"new breast change|impinduka mu ibere", 15),
]
MODS = [  # amplify only when a base signal exists
    ("Painless", r"painless|no pain|nta bubabare|ntibibabaza", 12),
    ("Growing / worsening", r"growing|bigger|getting worse|worsen|kwiyongera|rirakura", 15),
    ("Lasting weeks+", r"\d+\s*(?:weeks?|months?|ibyumweru|amezi)", 10),
    ("Family history", r"mother|sister|family history|nyina|mushiki|mu muryango", 12),
]
BARRIERS = {"transport": r"transport|\bfar\b|distance|urugendo|kure", "cost": r"money|cost|afford|amafaranga|mutuelle",
            "fear": r"afraid|fear|scared|ubwoba|mpangayitse", "stigma": r"shame|stigma|husband.*(?:refuse|angry)|isoni"}
WHEN = {"emergency": ("Now", "Ako kanya"), "urgent": ("Within 24-72 hours", "Mu masaha 24-72"),
        "needs_assessment": ("Within 1-2 weeks", "Mu byumweru 1-2"), "education": ("Routine", "Bisanzwe")}
MSG = {
 "emergency": ("Your message may describe an emergency. Please seek urgent in-person medical help now or contact local emergency services. Do not wait for this chat.",
  "Ubutumwa bwawe bushobora kugaragaza ikibazo cyihutirwa cyane. Shaka ubufasha bw'abaganga ako kanya cyangwa uhamagare serivisi z'ubutabazi. Ntutegereze iki kiganiro."),
 "urgent": ("This may need urgent medical assessment today, especially if symptoms are worsening or you have fever. Please contact a health professional or facility promptly.",
  "Ibi bishobora gusaba ko usuzumwa n'umuganga byihutirwa uyu munsi, cyane cyane niba birushaho kwiyongera cyangwa ufite umuriro. Vugana n'umuganga cyangwa ikigo nderabuzima vuba."),
 "needs_assessment": ("This breast change should be assessed by a qualified health professional. It does not automatically mean cancer, but it should not be ignored.",
  "Iyi mpinduka yo mu ibere ikwiye gusuzumwa n'umuganga ubifitiye ubushobozi. Ntibivuze ko ari kanseri byanze bikunze, ariko ntikwiye kwirengagizwa."),
 "education": ("I can provide breast-health education and help you decide the appropriate next step, but I cannot diagnose cancer.",
  "Nshobora gutanga amakuru ku buzima bw'amabere no kugufasha kumenya intambwe ikwiye gukurikira, ariko sinshobora gusuzuma kanseri.")}
PLAN = {
 "emergency": [("Go to the nearest emergency service now.", "Jya ku ivuriro ry'ubutabazi riri hafi ako kanya.")],
 "urgent": [("Contact a health facility today.", "Vugana n'ikigo nderabuzima uyu munsi."), ("Ask a navigator to book you a fast slot.", "Saba umuyobozi w'abarwayi (navigator) kuguteganyiriza vuba.")],
 "needs_assessment": [("Book a clinical breast exam at a health facility.", "Teganya gusuzumwa ibere ku kigo nderabuzima."), ("Note when it started and if it changed.", "Andika igihe byatangiriye n'uko byahindutse."), ("Request a human navigator to follow up.", "Saba navigator ngo agukurikirane.")],
 "education": [("Learn what is normal for your breasts.", "Menya uko amabere yawe asanzwe ameze."), ("Ask me anything about screening or referral.", "Mbaza ku isuzuma cyangwa koherezwa kwa muganga.")]}
TIPS = {"transport": ("Ask your community health worker about transport help.", "Baza umujyanama w'ubuzima ku bufasha bw'ingendo."),
        "cost": ("Ask the facility about Mutuelle de Santé or other coverage.", "Baza ikigo nderabuzima ku bwisungane mu kwivuza (Mutuelle)."),
        "fear": ("Feeling afraid is normal. A navigator can go through each step with you.", "Kugira ubwoba ni ibisanzwe. Navigator ashobora kugusobanurira buri ntambwe."),
        "stigma": ("You can ask for a private, respectful consultation.", "Ushobora gusaba kwakirwa mu ibanga no mu cyubahiro.")}

@dataclass
class TriageResult:
    level: str
    score: int = 0
    matched: List[str] = field(default_factory=list)
    barriers: List[str] = field(default_factory=list)
    safety_message_en: str = ""
    safety_message_rw: str = ""
    timeframe_en: str = ""
    timeframe_rw: str = ""
    plan_en: List[str] = field(default_factory=list)
    plan_rw: List[str] = field(default_factory=list)

def _has(p, t): return re.search(NEG + "(?:" + p + ")", t, re.I)

def triage_text(text: str) -> TriageResult:
    t = text.lower().strip()
    hits = [(l, w) for l, p, w in SIGNALS if _has(p, t)]
    score = sum(w for _, w in hits)
    labels = [l for l, _ in hits]
    if hits:
        for l, p, w in MODS:
            if re.search(p, t): score += w; labels.append(l)
        m = re.search(r"(?:age|imyaka)\s*(\d{2})|(\d{2})\s*(?:years|yrs|yo|imyaka)", t)
        if m and int(m.group(1) or m.group(2)) >= 40: score += 10; labels.append("Age 40+")
    score = min(score, 99)
    level = "urgent" if score >= 75 else "needs_assessment" if score >= 25 else "education"
    if re.search(URGENT, t): level, score = "urgent", max(score, 75); labels.append("Urgent pattern")
    if re.search(EMERGENCY, t): level, score = "emergency", 100; labels.append("Emergency sign")
    bars = [b for b, p in BARRIERS.items() if re.search(p, t)]
    return TriageResult(level, score, labels, bars, *MSG[level], *WHEN[level],
        [a for a, _ in PLAN[level]] + [TIPS[b][0] for b in bars], [b for _, b in PLAN[level]] + [TIPS[b][1] for b in bars])

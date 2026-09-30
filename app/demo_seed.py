"""Optional FAKE demo data (DEMO_SEED=true) so the dashboard is not empty after a Render restart."""
from datetime import datetime, timedelta
from .models import Patient, Conversation, Referral

ROWS = [  # level, score, reason, barriers, hours_ago, status
    ("emergency", 100, "Emergency sign", "", 0.5, "pending"),
    ("urgent", 89, "Breast lump, Painless, Growing, Age 40+", "transport", 20, "contacted"),
    ("urgent", 77, "Bloody nipple discharge, Family history", "cost", 60, "pending"),
    ("needs_assessment", 50, "Breast lump, Underarm lump", "cost,fear", 30, "pending"),
    ("needs_assessment", 42, "Skin change, Lasting weeks+", "fear", 120, "scheduled"),
    ("education", 0, "", "", 5, "closed"),
]

def seed(db):
    if db.query(Patient).count():
        return
    for i, (lvl, sc, why, bar, ago, st) in enumerate(ROWS, 1):
        t = datetime.utcnow() - timedelta(hours=ago)
        p = Patient(public_id=f"BCIEA-P-DEMO{i:02d}", consent_given=True, created_at=t)
        db.add(p); db.flush()
        db.add(Conversation(patient_id=p.id, triage_level=lvl, risk_score=sc, barriers=bar, created_at=t))
        if lvl != "education":
            db.add(Referral(patient_id=p.id, reason="[DEMO] AI triage: " + why, priority=lvl, risk_score=sc, status=st, created_at=t))
    db.commit()

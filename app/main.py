import os
import json
from datetime import datetime
import secrets
from fastapi import FastAPI, Depends, HTTPException, Header
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from sqlalchemy import func
from .config import APP_NAME, ADMIN_KEY
from .database import Base, engine, get_db, SessionLocal
from .models import Patient, Conversation, Message, Referral, AuditLog, BroadcastMessage
from .schemas import ChatRequest, PatientCreate, ReferralCreate, ReferralUpdate, BroadcastCreate
from .assistant_engine import respond

Base.metadata.create_all(bind=engine)
if os.getenv("DEMO_SEED", "").lower() in ("1", "true"):
    from .demo_seed import seed
    with SessionLocal() as _db:
        seed(_db)
app = FastAPI(title=APP_NAME, version="0.1.0")
app.mount("/static", StaticFiles(directory=os.path.join(os.path.dirname(__file__), "static")), name="static")


def require_admin(x_admin_key: str = Header(default="")):
    if not secrets.compare_digest(x_admin_key, ADMIN_KEY):
        raise HTTPException(status_code=401, detail="Invalid admin key")


def audit(db: Session, action: str, entity_type: str = None, entity_id: str = None, detail: str = None, actor: str = "system"):
    db.add(AuditLog(actor=actor, action=action, entity_type=entity_type, entity_id=entity_id, detail=detail))
    db.commit()


@app.get("/")
def home():
    return FileResponse(os.path.join(os.path.dirname(__file__), "static", "index.html"))


@app.get("/portal")
def portal_page():
    return FileResponse(os.path.join(os.path.dirname(__file__), "static", "portal.html"))


@app.get("/api/news")
def news():
    with open(os.path.join(os.path.dirname(__file__), "knowledge", "news.json"), encoding="utf-8") as f:
        return json.load(f)


@app.get("/admin")
def admin_page():
    return FileResponse(os.path.join(os.path.dirname(__file__), "static", "admin.html"))


@app.get("/health")
def health():
    return {"ok": True, "app": APP_NAME}


@app.post("/api/patients")
def create_patient(payload: PatientCreate, db: Session = Depends(get_db)):
    public_id = "BCIEA-P-" + secrets.token_hex(4).upper()
    p = Patient(public_id=public_id, full_name=payload.full_name, phone=payload.phone,
                preferred_language=payload.preferred_language, consent_given=payload.consent_given)
    db.add(p); db.commit(); db.refresh(p)
    audit(db, "patient_created", "patient", p.public_id, "Patient profile created")
    return {"public_id": p.public_id, "consent_given": p.consent_given}


@app.post("/api/chat")
async def chat(payload: ChatRequest, db: Session = Depends(get_db)):
    patient = None
    if payload.patient_public_id:
        patient = db.query(Patient).filter(Patient.public_id == payload.patient_public_id).first()
    conversation = None
    if payload.conversation_id:
        conversation = db.query(Conversation).filter(Conversation.id == payload.conversation_id).first()
    if not conversation:
        conversation = Conversation(patient_id=patient.id if patient else None, language=payload.language)
        db.add(conversation); db.commit(); db.refresh(conversation)
    db.add(Message(conversation_id=conversation.id, role="user", content=payload.message)); db.commit()
    result = await respond(payload.message, payload.language)
    conversation.triage_level = result["triage_level"]
    conversation.risk_score = result["risk_score"]
    conversation.barriers = ",".join(result["barriers"])
    db.add(Message(conversation_id=conversation.id, role="assistant", content=result["response"])); db.commit()
    if result["human_handoff_recommended"]:
        audit(db, "handoff_recommended", "conversation", str(conversation.id), result["triage_level"])
    return {"conversation_id": conversation.id, **result}


@app.post("/api/referrals")
def create_referral(payload: ReferralCreate, db: Session = Depends(get_db)):
    patient = db.query(Patient).filter(Patient.public_id == payload.patient_public_id).first()
    if not patient:
        raise HTTPException(404, "Patient not found")
    referral = Referral(patient_id=patient.id, reason=payload.reason, priority=payload.priority, facility=payload.facility, risk_score=payload.risk_score)
    db.add(referral); db.commit(); db.refresh(referral)
    audit(db, "referral_created", "referral", str(referral.id), payload.reason)
    return {"id": referral.id, "status": referral.status, "priority": referral.priority}


SLA_H = {"emergency": 1, "urgent": 48, "needs_assessment": 336, "education": 720}
RANK = {"emergency": 0, "urgent": 1, "needs_assessment": 2, "education": 3}
OPEN = ["pending", "contacted", "scheduled"]


def hours_left(r):
    return round(SLA_H.get(r.priority, 336) - (datetime.utcnow() - r.created_at).total_seconds() / 3600, 1)


@app.get("/api/admin/stats", dependencies=[Depends(require_admin)])
def admin_stats(db: Session = Depends(get_db)):
    convs = db.query(Conversation).all()
    barriers = {}
    for c in convs:
        for b in filter(None, (c.barriers or "").split(",")):
            barriers[b] = barriers.get(b, 0) + 1
    scores = [c.risk_score for c in convs if c.risk_score]
    pend = db.query(Referral).filter(Referral.status == "pending").all()
    return {
        "patients": db.query(func.count(Patient.id)).scalar(),
        "consented_cases": db.query(func.count(Patient.id)).filter(Patient.consent_given == True).scalar(),
        "conversations": len(convs),
        "messages": db.query(func.count(Message.id)).scalar(),
        "referrals": db.query(func.count(Referral.id)).scalar(),
        "pending_referrals": len(pend),
        "overdue": sum(1 for r in pend if hours_left(r) < 0),
        "avg_risk": round(sum(scores) / len(scores)) if scores else 0,
        "barriers": barriers,
        "triage": {l: sum(1 for c in convs if c.triage_level == l) for l in RANK},
    }


@app.get("/api/admin/referrals", dependencies=[Depends(require_admin)])
def list_referrals(db: Session = Depends(get_db)):
    rows = db.query(Referral).order_by(Referral.created_at.desc()).limit(200).all()
    # Priority-queue: open cases first -> clinical priority -> higher risk -> oldest
    rows.sort(key=lambda r: (r.status not in OPEN, RANK.get(r.priority, 2), -(r.risk_score or 0), r.created_at))
    return [{
        "id": r.id, "patient_public_id": r.patient.public_id, "reason": r.reason, "priority": r.priority,
        "status": r.status, "facility": r.facility, "navigator_notes": r.navigator_notes,
        "risk_score": r.risk_score or 0, "hours_left": hours_left(r) if r.status in OPEN else None,
        "created_at": r.created_at.isoformat(),
    } for r in rows]


@app.patch("/api/admin/referrals/{referral_id}", dependencies=[Depends(require_admin)])
def update_referral(referral_id: int, payload: ReferralUpdate, db: Session = Depends(get_db)):
    r = db.query(Referral).filter(Referral.id == referral_id).first()
    if not r:
        raise HTTPException(404, "Referral not found")
    for key, value in payload.model_dump(exclude_none=True).items():
        setattr(r, key, value)
    db.commit(); db.refresh(r)
    audit(db, "referral_updated", "referral", str(r.id), str(payload.model_dump(exclude_none=True)), actor="admin")
    return {"ok": True, "id": r.id, "status": r.status}


@app.get("/api/admin/audit", dependencies=[Depends(require_admin)])
def list_audit(db: Session = Depends(get_db)):
    rows = db.query(AuditLog).order_by(AuditLog.created_at.desc()).limit(100).all()
    return [{"actor": x.actor, "action": x.action, "entity_type": x.entity_type, "entity_id": x.entity_id, "detail": x.detail, "created_at": x.created_at.isoformat()} for x in rows]


@app.get("/api/admin/conversations", dependencies=[Depends(require_admin)])
def list_conversations(db: Session = Depends(get_db)):
    rows = db.query(Conversation).order_by(Conversation.created_at.desc()).limit(100).all()
    output = []
    for c in rows:
        last_message = db.query(Message).filter(Message.conversation_id == c.id).order_by(Message.created_at.desc()).first()
        count = db.query(func.count(Message.id)).filter(Message.conversation_id == c.id).scalar() or 0
        patient_public_id = None
        if c.patient_id:
            patient = db.query(Patient).filter(Patient.id == c.patient_id).first()
            patient_public_id = patient.public_id if patient else None
        output.append({
            "id": c.id, "patient_public_id": patient_public_id, "language": c.language,
            "triage_level": c.triage_level, "risk_score": c.risk_score or 0,
            "barriers": [x for x in (c.barriers or "").split(",") if x], "message_count": count,
            "last_message": (last_message.content[:180] if last_message else ""),
            "last_role": (last_message.role if last_message else None),
            "created_at": c.created_at.isoformat(),
        })
    return output


@app.get("/api/admin/conversations/{conversation_id}/messages", dependencies=[Depends(require_admin)])
def conversation_messages(conversation_id: int, db: Session = Depends(get_db)):
    c = db.query(Conversation).filter(Conversation.id == conversation_id).first()
    if not c:
        raise HTTPException(404, "Conversation not found")
    rows = db.query(Message).filter(Message.conversation_id == conversation_id).order_by(Message.created_at.asc()).all()
    return [{"role": m.role, "content": m.content, "created_at": m.created_at.isoformat()} for m in rows]


@app.get("/api/admin/patients", dependencies=[Depends(require_admin)])
def list_patients(db: Session = Depends(get_db)):
    rows = db.query(Patient).order_by(Patient.created_at.desc()).limit(100).all()
    return [{
        "public_id": p.public_id, "preferred_language": p.preferred_language,
        "consent_given": bool(p.consent_given), "has_name": bool(p.full_name), "has_phone": bool(p.phone),
        "referrals": len(p.referrals), "created_at": p.created_at.isoformat()
    } for p in rows]


@app.get("/api/admin/broadcasts", dependencies=[Depends(require_admin)])
def list_broadcasts(db: Session = Depends(get_db)):
    rows = db.query(BroadcastMessage).order_by(BroadcastMessage.created_at.desc()).limit(100).all()
    return [{
        "id": x.id, "title": x.title, "body": x.body, "audience": x.audience,
        "channel": x.channel, "status": x.status, "created_at": x.created_at.isoformat(),
        "sent_at": x.sent_at.isoformat() if x.sent_at else None
    } for x in rows]


@app.post("/api/admin/broadcasts", dependencies=[Depends(require_admin)])
def create_broadcast(payload: BroadcastCreate, db: Session = Depends(get_db)):
    status = "sent" if payload.send_now else "draft"
    row = BroadcastMessage(
        title=payload.title, body=payload.body, audience=payload.audience, channel=payload.channel,
        status=status, sent_at=datetime.utcnow() if payload.send_now else None
    )
    db.add(row); db.commit(); db.refresh(row)
    audit(db, "broadcast_" + status, "broadcast", str(row.id), f"{payload.channel}:{payload.audience}", actor="admin")
    return {"id": row.id, "status": row.status}

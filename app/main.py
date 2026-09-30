import os
import secrets
from fastapi import FastAPI, Depends, HTTPException, Header
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from sqlalchemy import func
from .config import APP_NAME, ADMIN_KEY
from .database import Base, engine, get_db
from .models import Patient, Conversation, Message, Referral, AuditLog
from .schemas import ChatRequest, PatientCreate, ReferralCreate, ReferralUpdate
from .assistant_engine import respond

Base.metadata.create_all(bind=engine)
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
    db.add(Message(conversation_id=conversation.id, role="assistant", content=result["response"])); db.commit()
    if result["human_handoff_recommended"]:
        audit(db, "handoff_recommended", "conversation", str(conversation.id), result["triage_level"])
    return {"conversation_id": conversation.id, **result}


@app.post("/api/referrals")
def create_referral(payload: ReferralCreate, db: Session = Depends(get_db)):
    patient = db.query(Patient).filter(Patient.public_id == payload.patient_public_id).first()
    if not patient:
        raise HTTPException(404, "Patient not found")
    referral = Referral(patient_id=patient.id, reason=payload.reason, priority=payload.priority, facility=payload.facility)
    db.add(referral); db.commit(); db.refresh(referral)
    audit(db, "referral_created", "referral", str(referral.id), payload.reason)
    return {"id": referral.id, "status": referral.status, "priority": referral.priority}


@app.get("/api/admin/stats", dependencies=[Depends(require_admin)])
def admin_stats(db: Session = Depends(get_db)):
    return {
        "patients": db.query(func.count(Patient.id)).scalar(),
        "conversations": db.query(func.count(Conversation.id)).scalar(),
        "referrals": db.query(func.count(Referral.id)).scalar(),
        "pending_referrals": db.query(func.count(Referral.id)).filter(Referral.status == "pending").scalar(),
        "triage": {lvl: db.query(func.count(Conversation.id)).filter(Conversation.triage_level == lvl).scalar() for lvl in ["education", "needs_assessment", "urgent", "emergency"]},
    }


@app.get("/api/admin/referrals", dependencies=[Depends(require_admin)])
def list_referrals(db: Session = Depends(get_db)):
    rows = db.query(Referral).order_by(Referral.created_at.desc()).limit(200).all()
    return [{
        "id": r.id,
        "patient_public_id": r.patient.public_id,
        "reason": r.reason,
        "priority": r.priority,
        "status": r.status,
        "facility": r.facility,
        "navigator_notes": r.navigator_notes,
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

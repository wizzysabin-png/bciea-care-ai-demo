from typing import Optional
from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=4000)
    language: str = "rw"
    conversation_id: Optional[int] = None
    patient_public_id: Optional[str] = None


class PatientCreate(BaseModel):
    full_name: Optional[str] = None
    phone: Optional[str] = None
    preferred_language: str = "rw"
    consent_given: bool = False


class ReferralCreate(BaseModel):
    patient_public_id: str
    reason: str
    priority: str = "needs_assessment"
    facility: Optional[str] = None
    risk_score: int = 0


class ReferralUpdate(BaseModel):
    status: Optional[str] = None
    facility: Optional[str] = None
    navigator_notes: Optional[str] = None


class BroadcastCreate(BaseModel):
    title: str = Field(min_length=1, max_length=180)
    body: str = Field(min_length=1, max_length=4000)
    audience: str = Field(default="all", max_length=80)
    channel: str = Field(default="in_app", max_length=40)
    send_now: bool = False

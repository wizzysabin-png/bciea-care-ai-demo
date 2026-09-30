from datetime import datetime
from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship
from .database import Base


class Patient(Base):
    __tablename__ = "patients"
    id = Column(Integer, primary_key=True)
    public_id = Column(String(32), unique=True, index=True, nullable=False)
    full_name = Column(String(120), nullable=True)
    phone = Column(String(40), nullable=True)
    preferred_language = Column(String(12), default="rw")
    consent_given = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    referrals = relationship("Referral", back_populates="patient")


class Conversation(Base):
    __tablename__ = "conversations"
    id = Column(Integer, primary_key=True)
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=True)
    language = Column(String(12), default="rw")
    triage_level = Column(String(32), default="education")
    created_at = Column(DateTime, default=datetime.utcnow)


class Message(Base):
    __tablename__ = "messages"
    id = Column(Integer, primary_key=True)
    conversation_id = Column(Integer, ForeignKey("conversations.id"), nullable=False)
    role = Column(String(20), nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)


class Referral(Base):
    __tablename__ = "referrals"
    id = Column(Integer, primary_key=True)
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False)
    reason = Column(Text, nullable=False)
    priority = Column(String(32), default="needs_assessment")
    status = Column(String(32), default="pending")
    facility = Column(String(160), nullable=True)
    navigator_notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    patient = relationship("Patient", back_populates="referrals")


class AuditLog(Base):
    __tablename__ = "audit_logs"
    id = Column(Integer, primary_key=True)
    actor = Column(String(100), default="system")
    action = Column(String(120), nullable=False)
    entity_type = Column(String(80), nullable=True)
    entity_id = Column(String(80), nullable=True)
    detail = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

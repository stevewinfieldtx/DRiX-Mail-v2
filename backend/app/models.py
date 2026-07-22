import enum, uuid
from datetime import datetime, timezone
from sqlalchemy import String, Text, DateTime, Boolean, ForeignKey, Integer, Float, JSON, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .database import Base

def uid(): return str(uuid.uuid4())
def now(): return datetime.now(timezone.utc)

class ClientStatus(str, enum.Enum): draft="draft"; approved="approved"
class ProspectStatus(str, enum.Enum): new="new"; researched="researched"; ready="ready"; waiting="waiting"; replied="replied"; meeting="meeting"; closed="closed"; suppressed="suppressed"; error="error"
class EvidenceKind(str, enum.Enum): verified_fact="verified_fact"; supported_inference="supported_inference"; industry_pattern="industry_pattern"; unknown="unknown"
class ReplyKind(str, enum.Enum): positive_interest="positive_interest"; request_for_information="request_for_information"; referral="referral"; objection="objection"; timing_issue="timing_issue"; not_relevant="not_relevant"; unsubscribe="unsubscribe"; out_of_office="out_of_office"; automated_response="automated_response"; unknown="unknown"
class EmailStatus(str, enum.Enum): ready="ready"; exported="exported"; sent="sent"; stopped="stopped"

class Client(Base):
    __tablename__="clients"
    id: Mapped[str]=mapped_column(String(36), primary_key=True, default=uid)
    name: Mapped[str]=mapped_column(String(160)); main_url: Mapped[str]=mapped_column(String(500))
    extra_urls: Mapped[list]=mapped_column(JSON, default=list); source_texts: Mapped[list]=mapped_column(JSON, default=list)
    profile: Mapped[dict]=mapped_column(JSON, default=dict); status: Mapped[ClientStatus]=mapped_column(Enum(ClientStatus), default=ClientStatus.draft)
    created_at: Mapped[datetime]=mapped_column(DateTime(timezone=True), default=now)
    campaigns: Mapped[list["Campaign"]]=relationship(back_populates="client", cascade="all, delete-orphan")

class Campaign(Base):
    __tablename__="campaigns"
    id: Mapped[str]=mapped_column(String(36), primary_key=True, default=uid); client_id: Mapped[str]=mapped_column(ForeignKey("clients.id"))
    name: Mapped[str]=mapped_column(String(160)); target_audience: Mapped[str]=mapped_column(Text); personas: Mapped[list]=mapped_column(JSON, default=list)
    narrative_strategy: Mapped[str]=mapped_column(Text, default="auto"); blueprint_template: Mapped[list]=mapped_column(JSON, default=list)
    cadence_days: Mapped[list]=mapped_column(JSON, default=lambda:[0,3,4,5,7]); stop_conditions: Mapped[list]=mapped_column(JSON, default=lambda:["positive_interest","not_relevant","unsubscribe"])
    subject_strategy: Mapped[str]=mapped_column(Text, default="observation, pattern, contrast, prediction, consequence, or curiosity")
    cta_rules: Mapped[dict]=mapped_column(JSON, default=dict); active: Mapped[bool]=mapped_column(Boolean, default=True)
    client: Mapped[Client]=relationship(back_populates="campaigns"); prospects: Mapped[list["Prospect"]]=relationship(back_populates="campaign", cascade="all, delete-orphan")

class Prospect(Base):
    __tablename__="prospects"
    id: Mapped[str]=mapped_column(String(36), primary_key=True, default=uid); campaign_id: Mapped[str]=mapped_column(ForeignKey("campaigns.id"))
    company_url: Mapped[str]=mapped_column(String(500)); company_name: Mapped[str]=mapped_column(String(160), default="")
    contact_name: Mapped[str]=mapped_column(String(160), default=""); contact_title: Mapped[str]=mapped_column(String(160), default=""); contact_email: Mapped[str]=mapped_column(String(320), default="")
    linkedin_url: Mapped[str]=mapped_column(String(500), default=""); extra_urls: Mapped[list]=mapped_column(JSON, default=list); notes: Mapped[str]=mapped_column(Text, default=""); custom_fields: Mapped[dict]=mapped_column(JSON, default=dict)
    status: Mapped[ProspectStatus]=mapped_column(Enum(ProspectStatus), default=ProspectStatus.new); stage: Mapped[int]=mapped_column(Integer, default=0)
    confidence: Mapped[float]=mapped_column(Float, default=0); strategic_brief: Mapped[dict]=mapped_column(JSON, default=dict); blueprint: Mapped[list]=mapped_column(JSON, default=list)
    reply_status: Mapped[str]=mapped_column(String(60), default=""); next_action: Mapped[str]=mapped_column(String(120), default="research prospect"); due_at: Mapped[datetime|None]=mapped_column(DateTime(timezone=True), nullable=True); external_campaign_id: Mapped[str]=mapped_column(String(160), default="")
    created_at: Mapped[datetime]=mapped_column(DateTime(timezone=True), default=now); campaign: Mapped[Campaign]=relationship(back_populates="prospects")
    evidence: Mapped[list["Evidence"]]=relationship(back_populates="prospect", cascade="all, delete-orphan"); emails: Mapped[list["Email"]]=relationship(back_populates="prospect", cascade="all, delete-orphan")

class Evidence(Base):
    __tablename__="evidence"
    id: Mapped[str]=mapped_column(String(36), primary_key=True, default=uid); prospect_id: Mapped[str]=mapped_column(ForeignKey("prospects.id"))
    source: Mapped[str]=mapped_column(String(1000)); fact: Mapped[str]=mapped_column(Text); evidence_type: Mapped[str]=mapped_column(String(80)); confidence: Mapped[float]=mapped_column(Float)
    kind: Mapped[EvidenceKind]=mapped_column(Enum(EvidenceKind)); observed_at: Mapped[datetime]=mapped_column(DateTime(timezone=True), default=now); volatile: Mapped[bool]=mapped_column(Boolean, default=False)
    prospect: Mapped[Prospect]=relationship(back_populates="evidence")

class Email(Base):
    __tablename__="emails"
    id: Mapped[str]=mapped_column(String(36), primary_key=True, default=uid); prospect_id: Mapped[str]=mapped_column(ForeignKey("prospects.id"))
    number: Mapped[int]=mapped_column(Integer); subject: Mapped[str]=mapped_column(String(300)); body: Mapped[str]=mapped_column(Text); cta: Mapped[str]=mapped_column(String(500))
    status: Mapped[EmailStatus]=mapped_column(Enum(EmailStatus), default=EmailStatus.ready); generated_at: Mapped[datetime]=mapped_column(DateTime(timezone=True), default=now); sent_at: Mapped[datetime|None]=mapped_column(DateTime(timezone=True), nullable=True)
    narrative_type: Mapped[str]=mapped_column(String(80), default=""); primary_business_outcome: Mapped[str]=mapped_column(String(300), default=""); proof_used: Mapped[str]=mapped_column(Text, default=""); research_summary: Mapped[str]=mapped_column(Text, default=""); thread_subject: Mapped[str]=mapped_column(String(300), default=""); sequence_id: Mapped[str]=mapped_column(String(80), default=uid)
    prospect: Mapped[Prospect]=relationship(back_populates="emails")

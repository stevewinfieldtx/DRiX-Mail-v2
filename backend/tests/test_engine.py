from types import SimpleNamespace
import pytest
from app.engine import kind_for, usable_claim, classify_reply, generate_next, apply_reply, enforce_email_limits, fit_email_to_band
from app.models import EvidenceKind, Evidence, ProspectStatus, EmailStatus

def test_confidence_boundaries():
    assert kind_for(.95)==EvidenceKind.verified_fact
    assert kind_for(.80)==EvidenceKind.supported_inference
    assert kind_for(.60)==EvidenceKind.industry_pattern
    assert kind_for(.49)==EvidenceKind.unknown

def test_unknown_evidence_is_never_usable():
    e=Evidence(confidence=.49,kind=EvidenceKind.unknown,source="x",fact="claim",evidence_type="test",prospect_id="p")
    assert not usable_claim(e)

@pytest.mark.parametrize("text,kind",[("Please unsubscribe","unsubscribe"),("I am out of office","out_of_office"),("Let's book a meeting","positive_interest"),("Send more information","request_for_information")])
def test_reply_classification(text,kind): assert classify_reply(text)==kind

class DB:
    def __init__(self):self.added=[]
    def add(self,x):self.added.append(x)
    def commit(self):pass
    def refresh(self,x):pass

def prospect():
    profile={"business_outcomes":["predictable growth"],"cta_library":["Open to comparing notes?"],"proof":[]}
    campaign=SimpleNamespace(client=SimpleNamespace(profile=profile),cadence_days=[0,3,4,5,7],stop_conditions=["unsubscribe"])
    return SimpleNamespace(id="p",status=ProspectStatus.researched,stage=0,emails=[],campaign=campaign,strategic_brief={"mode":"evidence-light","research_summary":"Company-specific evidence is limited.","primary_business_outcome":"predictable growth","proof":""},blueprint=[{"chapter":x} for x in ["future","friction","cost","path","decision"]],company_name="Thin Startup",next_action="")

def test_generates_only_one_next_email(monkeypatch):
    monkeypatch.setattr("app.engine.llm_json",lambda *a,**k:None);p=prospect();db=DB();first=generate_next(db,p);p.emails.append(first);second=generate_next(db,p)
    assert first is second and len(db.added)==1

def test_evidence_light_copy_is_conditional(monkeypatch):
    monkeypatch.setattr("app.engine.llm_json",lambda *a,**k:None);e=generate_next(DB(),prospect())
    assert "often" in e.body and "I noticed" not in e.body

def test_generated_email_has_hard_length_and_subject_limits():
    long_body=" ".join(["Roadmap pressure can consume engineering attention and delay customer learning."]*14)
    subject,body=enforce_email_limits("A very long personalized subject line here",long_body,"Worth a brief conversation?","")
    assert len(subject.split())<=4
    assert len(body.split())<=95
    assert body.endswith("Worth a brief conversation?")

def test_short_email_is_rewritten_or_falls_back_into_75_to_95_words(monkeypatch):
    monkeypatch.setattr("app.engine.llm_json",lambda *a,**k:None)
    p=prospect(); subject,body,cta=fit_email_to_band(p,1,"Funding signal","Your funding suggests growth.\n\nTalk to our team","Talk to our team",p.campaign.client.profile)
    assert 75<=len(body.split())<=95
    assert len(subject.split())<=4
    assert body.endswith(cta)
def test_unsupported_numbers_are_removed():
    source="Domestic engineers cost $180K and take 4 months to ramp. Engineering capacity can affect roadmap timing."
    _,body=enforce_email_limits("Hiring economics now",source,"Open to comparing notes?","")
    assert "$180K" not in body and "4 months" not in body
    assert "roadmap timing" in body
def test_existing_ready_email_is_normalized_when_reopened(monkeypatch):
    p=prospect(); existing=SimpleNamespace(status=EmailStatus.ready,number=1,subject="An unnecessarily long subject about engineering capacity",body=" ".join(["This is an overly long sentence about delivery capacity."]*20),cta="Open to comparing notes?",thread_subject="")
    p.emails=[existing]; returned=generate_next(DB(),p)
    assert returned is existing
    assert len(returned.subject.split())<=4
    assert 75<=len(returned.body.split())<=95
def test_stop_condition_blocks_generation(monkeypatch):
    p=prospect();p.status=ProspectStatus.suppressed
    with pytest.raises(ValueError,match="stopped"):generate_next(DB(),p)

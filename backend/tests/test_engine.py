from types import SimpleNamespace
import pytest
from app.engine import kind_for, usable_claim, classify_reply, generate_next, apply_reply
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

def test_stop_condition_blocks_generation(monkeypatch):
    p=prospect();p.status=ProspectStatus.suppressed
    with pytest.raises(ValueError,match="stopped"):generate_next(DB(),p)

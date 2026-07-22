import json, re
from datetime import datetime, timezone, timedelta
from urllib.parse import urlparse
import httpx
from bs4 import BeautifulSoup
from openai import OpenAI
from sqlalchemy.orm import Session
from .config import settings
from .models import Client, Campaign, Prospect, Evidence, EvidenceKind, Email, EmailStatus, ProspectStatus, ReplyKind

DEFAULT_CTAS=["Open to comparing notes?","Worth a brief conversation?","Should I send a short example?","Is this on your roadmap?","Are you the right person for this?"]
BLUEPRINT=[
 {"stage":1,"chapter":"The future","purpose":"Show the opportunity or direction already visible."},
 {"stage":2,"chapter":"The friction","purpose":"Explain the hidden constraint without asserting an unverified pain."},
 {"stage":3,"chapter":"The cost","purpose":"Connect the constraint to money, time, risk, or peace of mind."},
 {"stage":4,"chapter":"The alternate path","purpose":"Use the closest credible proof and show what better looks like."},
 {"stage":5,"chapter":"The decision","purpose":"Create a timely, low-pressure reason to talk."},
]

def kind_for(confidence:float, direct:bool=True):
    if direct and confidence>=.95: return EvidenceKind.verified_fact
    if confidence>=.75: return EvidenceKind.supported_inference
    if confidence>=.50: return EvidenceKind.industry_pattern
    return EvidenceKind.unknown

def usable_claim(e:Evidence): return e.kind != EvidenceKind.unknown and e.confidence >= .50

def fetch_text(url:str)->str:
    try:
        r=httpx.get(url,timeout=12,follow_redirects=True,headers={"User-Agent":"NarrativePlatform/1.0"}); r.raise_for_status()
        soup=BeautifulSoup(r.text,"html.parser")
        for tag in soup(["script","style","nav","footer"]): tag.decompose()
        return " ".join(soup.get_text(" ",strip=True).split())[:30000]
    except Exception: return ""

def llm_json(system:str, payload:dict, strong=False):
    if not settings.openai_api_key: return None
    client=OpenAI(api_key=settings.openai_api_key)
    response=client.chat.completions.create(model=settings.strategy_model if strong else settings.extraction_model,response_format={"type":"json_object"},temperature=.2,messages=[{"role":"system","content":system},{"role":"user","content":json.dumps(payload)}])
    return json.loads(response.choices[0].message.content)

def build_seller_profile(client:Client)->dict:
    texts=[fetch_text(client.main_url)]+[fetch_text(x) for x in client.extra_urls]+client.source_texts
    material="\n".join(x for x in texts if x)
    prompt="Extract a grounded seller intelligence profile as JSON. Keys: summary,strengths,weaknesses,differentiators,services,proof,ideal_customers,prohibited_claims,tone,business_outcomes,outcome_map,cta_library. Never invent claims; mark weak evidence in weaknesses."
    ai=llm_json(prompt,{"name":client.name,"urls":[client.main_url,*client.extra_urls],"material":material[:80000]})
    if ai: return ai
    domain=urlparse(client.main_url).netloc or client.name
    return {"summary":f"{client.name} seller profile grounded in supplied materials from {domain}.","strengths":["Client-supplied positioning can be translated into outcome-led outreach"],"weaknesses":["Limited independently verified proof until case studies are supplied"],"differentiators":[],"services":[],"proof":[],"ideal_customers":[],"prohibited_claims":["Unverified performance, customer, financial, compliance, or comparative claims"],"tone":"credible, concise, consultative","business_outcomes":["revenue growth","lower risk","time saved","greater predictability","executive peace of mind"],"outcome_map":[],"cta_library":DEFAULT_CTAS}

def research(db:Session,p:Prospect):
    urls=[p.company_url,*p.extra_urls]; records=[]
    for url in urls:
        text=fetch_text(url)
        if text:
            name=p.company_name or urlparse(url).netloc.split(".")[0].title()
            fact=f"{name} publicly describes its offering on its website: {text[:360]}"
            records.append(Evidence(prospect_id=p.id,source=url,fact=fact,evidence_type="company_website",confidence=.96,kind=EvidenceKind.verified_fact,volatile=False))
    if p.notes:
        records.append(Evidence(prospect_id=p.id,source="operator_notes",fact=p.notes,evidence_type="provided_context",confidence=.90,kind=EvidenceKind.supported_inference,volatile=False))
    if not records:
        records.append(Evidence(prospect_id=p.id,source="business_model_pattern",fact="Public company-specific evidence is limited; messaging must use conditional business-model or industry patterns.",evidence_type="fallback_guardrail",confidence=.65,kind=EvidenceKind.industry_pattern,volatile=False))
    db.add_all(records); db.flush()
    usable=[e for e in records if usable_claim(e)]; p.confidence=round(sum(e.confidence for e in usable)/max(1,len(usable)),2)
    seller=p.campaign.client.profile; top=usable[0].fact if usable else "Company-specific evidence is limited."
    outcome=(seller.get("business_outcomes") or ["more predictable business execution"])[0]
    p.strategic_brief={"research_summary":top,"strategic_intersection":f"Connect the prospect's observable context to {outcome}, using only approved seller capabilities.","primary_business_outcome":outcome,"proof":(seller.get("proof") or [""])[0],"confidence":p.confidence,"mode":"evidence-rich" if any(e.kind==EvidenceKind.verified_fact for e in records) else "evidence-light","do_not_claim":["Unverified company pain, hiring, funding, technology, performance, intent, or urgency"]}
    p.blueprint=[dict(x, angle=(top if x["stage"]==1 else x["purpose"])) for x in BLUEPRINT]
    p.status=ProspectStatus.researched; p.next_action="generate email 1"; db.commit(); return p

def _local_email(p:Prospect,stage:int,cta:str):
    brief=p.strategic_brief; company=p.company_name or "your team"; mode=brief.get("mode")
    observable=brief.get("research_summary","")
    if mode=="evidence-rich": opening=f"Your public positioning suggests {observable.split(':',1)[-1].strip()[:180]}"
    else: opening=f"Companies building businesses like {company} often reach a point where execution capacity shapes what can happen next."
    outcome=brief.get("primary_business_outcome","more predictable execution")
    subjects=["The constraint behind the next stage","When sensible growth creates friction","The cost that never gets its own line item","A more predictable path forward","The decision before the bottleneck"]
    chapters=[
      f"{opening}\n\nThe interesting question is whether the operating model can keep pace with that ambition. We help teams connect execution to {outcome} without relying on unverified assumptions about what is happening inside the business.",
      f"Growth rarely breaks because the strategy is unclear. More often, normal operating friction compounds faster than teams expect. For {company}, the useful conversation may be how to preserve momentum while keeping risk and distraction contained.",
      f"The visible cost of a constraint is usually capacity. The larger cost is delayed learning: decisions, customer feedback, and revenue arrive later. That is why {outcome} is often an operating issue before it becomes a budget issue.",
      f"A better path is not simply adding more activity. It is making execution more predictable, with clear ownership and evidence the approach fits the business. That is the outcome our work is designed to support.",
      f"Timing matters because small constraints become expensive only after they compound. If {outcome} is relevant this year, a short comparison now may be more useful than a larger intervention later."
    ]
    return subjects[stage-1], chapters[stage-1]+"\n\n"+cta

def generate_next(db:Session,p:Prospect):
    if p.status in {ProspectStatus.replied,ProspectStatus.closed,ProspectStatus.suppressed,ProspectStatus.meeting}: raise ValueError("Sequence is stopped")
    ready=next((e for e in p.emails if e.status==EmailStatus.ready),None)
    if ready: return ready
    stage=p.stage+1
    if stage>5: p.status=ProspectStatus.closed; p.next_action="sequence complete"; db.commit(); raise ValueError("Sequence complete")
    profile=p.campaign.client.profile; ctas=profile.get("cta_library") or DEFAULT_CTAS; cta=ctas[min(stage-1,len(ctas)-1)]
    history=[{"number":e.number,"subject":e.subject,"body":e.body} for e in sorted(p.emails,key=lambda x:x.number)]
    rule="Write one concise B2B email as JSON subject,body,cta. Ground every company-specific assertion in evidence. For inference use conditional language. Never invent facts. Subject uses observation/pattern/contrast/prediction/consequence/curiosity and not a name token. Continue the blueprint without repeating prior email."
    ai=llm_json(rule,{"seller":profile,"prospect":p.strategic_brief,"blueprint":p.blueprint,"stage":stage,"history":history,"selected_cta":cta},strong=True)
    subject,body=(ai.get("subject"),ai.get("body")) if ai else _local_email(p,stage,cta)
    if ai: cta=ai.get("cta",cta); body=body.rstrip()+"\n\n"+cta if cta not in body else body
    e=Email(prospect_id=p.id,number=stage,subject=subject[:300],body=body,cta=cta,narrative_type=p.blueprint[stage-1]["chapter"],primary_business_outcome=p.strategic_brief.get("primary_business_outcome",""),proof_used=p.strategic_brief.get("proof",""),research_summary=p.strategic_brief.get("research_summary",""),thread_subject=subject)
    db.add(e); p.status=ProspectStatus.ready; p.next_action=f"send/export email {stage}"; db.commit(); db.refresh(e); return e

def mark_sent(db:Session,e:Email):
    e.status=EmailStatus.sent; e.sent_at=datetime.now(timezone.utc); p=e.prospect; p.stage=e.number; p.status=ProspectStatus.waiting; days=p.campaign.cadence_days[min(e.number,len(p.campaign.cadence_days)-1)]; p.due_at=datetime.now(timezone.utc)+timedelta(days=days); p.next_action="wait for reply" if e.number==5 else f"generate email {e.number+1} when due"; db.commit(); return p

def classify_reply(text:str)->str:
    t=text.lower()
    rules=[("unsubscribe",["unsubscribe","remove me"]),("out_of_office",["out of office","away until"]),("referral",["speak with","contact my","right person"]),("positive_interest",["interested","book","meeting","let's talk","lets talk"]),("request_for_information",["send more","more information","details"]),("timing_issue",["not now","next quarter","later"]),("not_relevant",["not interested","not relevant"]),("automated_response",["automated response","do not reply"]),("objection",["already use","too expensive","no budget"])]
    return next((k for k,words in rules if any(w in t for w in words)),"unknown")

def apply_reply(db:Session,p:Prospect,kind:str):
    p.reply_status=kind
    if kind=="positive_interest": p.status=ProspectStatus.meeting; p.next_action="book meeting"
    elif kind in {"unsubscribe"}: p.status=ProspectStatus.suppressed; p.next_action="suppressed"
    elif kind in {"not_relevant"}: p.status=ProspectStatus.closed; p.next_action="closed"
    elif kind=="out_of_office": p.status=ProspectStatus.waiting; p.due_at=datetime.now(timezone.utc)+timedelta(days=7); p.next_action="resume after return"
    elif kind=="referral": p.status=ProspectStatus.replied; p.next_action="create referred contact"
    else: p.status=ProspectStatus.replied; p.next_action="send autonomous reply"
    for e in p.emails:
        if e.status==EmailStatus.ready: e.status=EmailStatus.stopped
    db.commit(); return p

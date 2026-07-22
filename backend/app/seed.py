from .database import Base,engine,SessionLocal
from .models import Client,Campaign,ClientStatus
from .engine import DEFAULT_CTAS

def seed():
    Base.metadata.create_all(engine); db=SessionLocal()
    if db.query(Client).count(): return
    for name,url,proof in [("FRAM","https://wearefram.com",["Tiptapp marketplace engineering partnership"]),("VIVA Software","https://vivasoftltd.com",[])]:
        c=Client(name=name,main_url=url,status=ClientStatus.approved,profile={"summary":f"Example approved profile for {name}; replace or regenerate from sources before production use.","strengths":["Dedicated software product delivery"],"weaknesses":["Proof must be confirmed from supplied case studies"],"differentiators":[],"services":["software product development"],"proof":proof,"ideal_customers":["startups and growth companies"],"prohibited_claims":["unverified outcomes or client names"],"tone":"credible, concise, consultative","business_outcomes":["faster, more predictable product delivery"],"outcome_map":["engineering capacity","release velocity","faster learning","growth"],"cta_library":DEFAULT_CTAS}); db.add(c); db.flush(); db.add(Campaign(client_id=c.id,name=f"{name} Startup Narrative",target_audience="Startup founders and technology leaders",personas=["Founder","CTO","VP Engineering"]))
    db.commit(); db.close()
if __name__=="__main__": seed()

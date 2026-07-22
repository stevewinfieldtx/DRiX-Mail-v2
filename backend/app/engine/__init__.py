"""Public engine facade with optional Targeted Decomposition enrichment."""
import importlib.util
from pathlib import Path

_spec=importlib.util.spec_from_file_location("app._engine_core",Path(__file__).parents[1]/"engine.py")
_core=importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_core)
for _name in dir(_core):
    if not _name.startswith("_"):globals()[_name]=getattr(_core,_name)

from ..tde import decompose

def research(db,p):
    p=_core.research(db,p)
    evidence=[{"source":e.source,"fact":e.fact,"kind":e.kind.value,"confidence":e.confidence} for e in p.evidence if _core.usable_claim(e)]
    result=decompose({"seller_profile":p.campaign.client.profile,"prospect":{"company_name":p.company_name,"company_url":p.company_url,"contact_title":p.contact_title},"evidence":evidence,"objective":"Find the most defensible seller-capability/prospect-opportunity intersection."})
    if result is not None:
        p.strategic_brief={**p.strategic_brief,"targeted_decomposition":result}
        db.commit()
    return p

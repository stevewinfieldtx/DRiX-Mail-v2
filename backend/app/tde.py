import os
import httpx

def decompose(payload:dict)->dict|None:
    """Targeted Decomposition Engine HTTP adapter.

    Configure TDE_BASE_URL and optional TDE_API_TOKEN. The engine is expected to
    expose POST /api/decompose and return a JSON object. Failures return None so
    the outbound pipeline remains available and evidence-safe.
    """
    base=os.getenv("TDE_BASE_URL")
    if not base:return None
    headers={"Content-Type":"application/json"}
    if token:=os.getenv("TDE_API_TOKEN"):headers["Authorization"]=f"Bearer {token}"
    try:
        r=httpx.post(f"{base.rstrip('/')}/api/decompose",json=payload,headers=headers,timeout=float(os.getenv("TDE_TIMEOUT_SECONDS","30")))
        r.raise_for_status();return r.json()
    except (httpx.HTTPError,ValueError):return None

from typing import Any
from pydantic import BaseModel, ConfigDict, EmailStr

class ORM(BaseModel): model_config=ConfigDict(from_attributes=True)
class ClientCreate(BaseModel): name:str; main_url:str; extra_urls:list[str]=[]
class ClientOut(ORM): id:str; name:str; main_url:str; extra_urls:list; profile:dict; status:str
class CampaignCreate(BaseModel): client_id:str; name:str; target_audience:str; personas:list[str]=[]; narrative_strategy:str="auto"; cadence_days:list[int]=[0,3,4,5,7]; stop_conditions:list[str]=["positive_interest","not_relevant","unsubscribe"]
class CampaignOut(ORM): id:str; client_id:str; name:str; target_audience:str; active:bool
class ProspectCreate(BaseModel): campaign_id:str; company_url:str; company_name:str=""; contact_name:str=""; contact_title:str=""; contact_email:str=""; linkedin_url:str=""; extra_urls:list[str]=[]; notes:str=""; custom_fields:dict[str,Any]={}; external_campaign_id:str=""
class ProspectOut(ORM): id:str; campaign_id:str; company_url:str; company_name:str; contact_name:str; contact_title:str; contact_email:str; status:str; stage:int; confidence:float; reply_status:str; next_action:str; strategic_brief:dict; blueprint:list
class EmailOut(ORM): id:str; prospect_id:str; number:int; subject:str; body:str; cta:str; status:str; narrative_type:str; primary_business_outcome:str
class ProfileUpdate(BaseModel): profile:dict[str,Any]
class ReplyIn(BaseModel): text:str; kind:str|None=None

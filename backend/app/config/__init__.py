import os
from pydantic_settings import BaseSettings,SettingsConfigDict

class Settings(BaseSettings):
    database_url:str="sqlite:///./narrative.db"
    openai_api_key:str|None=None
    openrouter_api_key:str|None=None
    openrouter_model_id:str|None=None
    openrouter_base_url:str="https://openrouter.ai/api/v1"
    extraction_model:str="gpt-4.1-mini"
    strategy_model:str="gpt-4.1"
    cors_origins:str="http://localhost:3000"
    model_config=SettingsConfigDict(env_file=".env",extra="ignore")

settings=Settings()

# Railway emits a generic PostgreSQL URL. Select the installed Psycopg 3
# dialect explicitly so production does not attempt to import psycopg2.
if settings.database_url.startswith("postgresql://"):
    settings.database_url=settings.database_url.replace("postgresql://","postgresql+psycopg://",1)

# The OpenAI SDK is protocol-compatible with OpenRouter. The existing model
# pipeline therefore stays provider-neutral while these values redirect it.
if settings.openrouter_api_key:
    settings.openai_api_key=settings.openrouter_api_key
    os.environ["OPENAI_BASE_URL"]=settings.openrouter_base_url
    if settings.openrouter_model_id:
        settings.extraction_model=settings.openrouter_model_id
        settings.strategy_model=settings.openrouter_model_id

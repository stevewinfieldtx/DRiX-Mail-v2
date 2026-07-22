from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    database_url: str = "sqlite:///./narrative.db"
    openai_api_key: str | None = None
    extraction_model: str = "gpt-4.1-mini"
    strategy_model: str = "gpt-4.1"
    cors_origins: str = "http://localhost:3000"
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()

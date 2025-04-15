from pydantic import BaseSettings
from functools import lru_cache
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Settings(BaseSettings):
    """Application settings."""
    # Database settings
    database_url: str = "sqlite+aiosqlite:///./tron_service.db"
    
    # TRON network settings
    tron_network: str = "mainnet"

    class Config:
        env_file = ".env"
        case_sensitive = False
        env_prefix = ""

@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
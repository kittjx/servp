from pydantic_settings import BaseSettings
from typing import Dict, Optional

class Settings(BaseSettings):
    DB_URL: Optional[str] = None
    class Config:
        case_sensitive = False

settings = Settings()

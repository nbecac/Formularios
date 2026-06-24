import os
from pathlib import Path
from pydantic_settings import BaseSettings
from typing import Optional
from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parents[2]
load_dotenv(PROJECT_ROOT / ".env", override=False)

class Settings(BaseSettings):
    """
    Configuraciones de entorno del backend (FastAPI).
    Permite inyectar claves de API por .env para el AI_PROVIDER.
    """
    API_PREFIX: str = "/api"
    DATABASE_URL: str = "sqlite:///./formularios.db"
    
    # Motor LLM a utilizar ('mock', 'openai', 'gemini')
    AI_PROVIDER: str = "gemini"
    AI_MODEL: str = "gemini-2.5-flash"
    
    OPENAI_API_KEY: Optional[str] = ""
    GEMINI_API_KEY: Optional[str] = ""
    GOOGLE_API_KEY: Optional[str] = ""
    ANTHROPIC_API_KEY: Optional[str] = ""
    
    BACKEND_HOST: str = "127.0.0.1"
    BACKEND_PORT: int = 8000
    
    @property
    def ACTIVE_GEMINI_KEY(self) -> str:
        if self.GEMINI_API_KEY:
            return self.GEMINI_API_KEY
        if self.GOOGLE_API_KEY:
            return self.GOOGLE_API_KEY
        return ""
    
    @property
    def GEMINI_KEY_SOURCE(self) -> str:
        if self.GEMINI_API_KEY:
            return "GEMINI_API_KEY"
        if self.GOOGLE_API_KEY:
            return "GOOGLE_API_KEY"
        return "missing"
    
    # Nuevas configuraciones de TAREA 4
    AUTHORIZED_EVALUATION_MODE: bool = False
    KNOWLEDGE_ONLY_MODE: bool = True
    ALLOW_EXTERNAL_AI: bool = False
    COURSE_PROJECT_MODE: bool = True
    
    class Config:
        env_file = ".env"

# Instancia global de configuraciones
settings = Settings()

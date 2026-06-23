from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    """
    Configuraciones de entorno del backend (FastAPI).
    Permite inyectar claves de API por .env para el AI_PROVIDER.
    """
    API_PREFIX: str = "/api"
    DATABASE_URL: str = "sqlite:///./formularios.db"
    
    # Motor LLM a utilizar ('mock', 'openai', 'gemini')
    AI_PROVIDER: str = "mock"
    AI_MODEL: str = "gpt-4o-mini"
    
    OPENAI_API_KEY: Optional[str] = ""
    GEMINI_API_KEY: Optional[str] = ""
    
    BACKEND_HOST: str = "127.0.0.1"
    BACKEND_PORT: int = 8000
    
    # Nuevas configuraciones de TAREA 4
    AUTHORIZED_EVALUATION_MODE: bool = False
    KNOWLEDGE_ONLY_MODE: bool = True
    ALLOW_EXTERNAL_AI: bool = False
    COURSE_PROJECT_MODE: bool = True
    
    class Config:
        env_file = ".env"

# Instancia global de configuraciones
settings = Settings()

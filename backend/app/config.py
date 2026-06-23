from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    """
    Configuraciones de entorno del backend (FastAPI).
    Permite inyectar claves de API por .env para el AI_PROVIDER.
    """
    API_PREFIX: str = "/api"
    DATABASE_URL: str = "sqlite:///./formularios.db"
    
    # Motor LLM a utilizar ('mock', 'openai', 'gemini')
    AI_PROVIDER: str = "mock"
    
    OPENAI_API_KEY: str = ""
    GEMINI_API_KEY: str = ""
    
    class Config:
        env_file = ".env"

# Instancia global de configuraciones
settings = Settings()

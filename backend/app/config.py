from pydantic_settings import BaseSettings
from pathlib import Path

# Calcular la ruta base del proyecto (2 niveles arriba de config.py)
BASE_DIR = Path(__file__).resolve().parent.parent.parent

class Settings(BaseSettings):
    AI_PROVIDER: str = "mock"
    AI_API_KEY: str = ""
    AI_MODEL: str = ""
    DATABASE_URL: str = f"sqlite:///{BASE_DIR / 'data' / 'formularios_agent.db'}"
    BACKEND_HOST: str = "127.0.0.1"
    BACKEND_PORT: int = 8000

    class Config:
        env_file = ".env"

settings = Settings()

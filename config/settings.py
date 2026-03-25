from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    TENANT_ID:     str
    CLIENT_ID:     str
    CLIENT_SECRET: str
    USUARIO:       str
    PASSWORD:      str
    NOMBRE_HOJA:   str = Field(default="Hoja1")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


try:
    settings = Settings()
except Exception as e:
    raise RuntimeError(f"Error cargando variables de entorno: {e}")
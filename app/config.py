from typing import Optional

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    IMAGE_BACKEND: Optional[str] = "dalle"
    STABILITY_API_KEY: Optional[str] = None
    OPENAI_API_KEY: Optional[str] = None

    class Config:
        env_file = ".env"


settings = Settings()

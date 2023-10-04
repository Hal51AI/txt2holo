from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    STABILITY_API_KEY: str
    OPENAI_API_KEY: str
    IMAGE_API: str = "dalle"

    class Config:
        env_file = ".env"


settings = Settings()

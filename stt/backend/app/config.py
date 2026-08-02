from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "postgresql://audiocopilot:audiocopilot@localhost:5432/audiocopilot"
    redis_url: str = "redis://localhost:6379/0"
    upload_dir: str = "uploads"
    whisper_model_size: str = "small"
    llm_provider: str = "gemini"
    gemini_api_key: str = ""
    cors_origins: str = "http://localhost:3000"
    log_level: str = "INFO"

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Database
    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/brd_pipeline"

    # Claude CLI
    claude_model: str = "sonnet"
    claude_timeout: int = 300

    # App
    app_env: str = "development"
    log_level: str = "INFO"
    upload_dir: str = "./uploads"
    max_upload_size_mb: int = 50

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()

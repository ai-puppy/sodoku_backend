from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "postgresql://username:password@localhost:5432/sudoku_db"
    secret_key: str = "your-secret-key-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    model_config = {"env_file": ".env"}


settings = Settings()

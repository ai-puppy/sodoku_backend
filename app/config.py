import os
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "postgresql://username:password@localhost:5432/sudoku_db"
    secret_key: str = "your-secret-key-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    model_config = {"env_file": ".env"}

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Override with environment variables if they exist (for Azure deployment)
        if os.getenv("DATABASE_URL"):
            self.database_url = os.getenv("DATABASE_URL")
        if os.getenv("SECRET_KEY"):
            self.secret_key = os.getenv("SECRET_KEY")
        if os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"):
            self.access_token_expire_minutes = int(
                os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES")
            )

        # Ensure SSL mode for Azure PostgreSQL connections
        if (
            "postgres.database.azure.com" in self.database_url
            and "sslmode=" not in self.database_url
        ):
            if "?" in self.database_url:
                self.database_url += "&sslmode=require"
            else:
                self.database_url += "?sslmode=require"


settings = Settings()

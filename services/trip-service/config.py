from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "postgresql://postgres:password@localhost:5432/trip_db"
    secret_key: str = "super-secret-key-change-in-production-123456"
    algorithm: str = "HS256"
    redis_url: str = "redis://localhost:6379"

    class Config:
        env_file = ".env"


settings = Settings()

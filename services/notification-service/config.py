from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "postgresql://postgres:password@localhost:5432/notification_db"
    secret_key: str = "super-secret-key"
    algorithm: str = "HS256"
    kafka_bootstrap_servers: str = "localhost:9092"
    smtp_host: str = "smtp.gmail.com"
    smtp_port: int = 587
    smtp_user: str = "noreply@busticket.com"
    smtp_password: str = "mock-password"

    class Config:
        env_file = ".env"


settings = Settings()

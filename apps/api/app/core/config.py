import os
from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = "NutriCore"
    app_env: str = "development"
    postgres_db: str = "starter"
    postgres_user: str = "starter"
    postgres_password: str = "starter_password"
    postgres_host: str = "postgres"
    postgres_port: int = 5432
    redis_host: str = "redis"
    redis_port: int = 6379
    redis_password: str | None = None
    jwt_secret: str = Field(default="change-this-jwt-secret", alias="NUTRICORE_JWT_SECRET")
    jwt_algorithm: str = Field(default="HS256", alias="NUTRICORE_JWT_ALGORITHM")
    jwt_access_token_expire_minutes: int = Field(
        default=60,
        alias="NUTRICORE_JWT_ACCESS_TOKEN_EXPIRE_MINUTES",
    )
    bootstrap_admin_email: str = Field(
        default="admin@nutricore.app",
        alias="NUTRICORE_BOOTSTRAP_ADMIN_EMAIL",
    )
    bootstrap_admin_password: str = Field(
        default="change-this-admin-password",
        alias="NUTRICORE_BOOTSTRAP_ADMIN_PASSWORD",
    )
    bootstrap_admin_name: str = Field(
        default="NutriCore Admin",
        alias="NUTRICORE_BOOTSTRAP_ADMIN_NAME",
    )
    bootstrap_admin_enabled: bool = Field(
        default=True,
        alias="NUTRICORE_BOOTSTRAP_ADMIN_ENABLED",
    )
    database_url: str | None = Field(default=None, alias="DATABASE_URL")
    cors_allowed_origins_raw: str = Field(
        default="http://web.localhost,http://web.localhost:8080,http://localhost:3000",
        alias="NUTRICORE_CORS_ALLOWED_ORIGINS",
    )

    @property
    def is_production(self) -> bool:
        return self.app_env.lower() == "production"

    @property
    def sqlalchemy_database_url(self) -> str:
        if self.database_url:
            if self.database_url.startswith("postgresql://"):
                return self.database_url.replace("postgresql://", "postgresql+psycopg://", 1)
            return self.database_url

        return (
            f"postgresql+psycopg://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )

    @property
    def postgres_dsn(self) -> str:
        return (
            f"dbname={self.postgres_db} user={self.postgres_user} "
            f"password={self.postgres_password} host={self.postgres_host} "
            f"port={self.postgres_port}"
        )

    @property
    def cors_allowed_origins(self) -> list[str]:
        return [
            origin.strip()
            for origin in self.cors_allowed_origins_raw.split(",")
            if origin.strip()
        ]


@lru_cache
def get_settings() -> Settings:
    return Settings(
        app_name=os.getenv("APP_NAME", "NutriCore"),
        app_env=os.getenv("APP_ENV", "development"),
        postgres_db=os.getenv("POSTGRES_DB", "starter"),
        postgres_user=os.getenv("POSTGRES_USER", "starter"),
        postgres_password=os.getenv("POSTGRES_PASSWORD", "starter_password"),
        postgres_host=os.getenv("POSTGRES_HOST", "postgres"),
        postgres_port=int(os.getenv("POSTGRES_PORT", "5432")),
        redis_host=os.getenv("REDIS_HOST", "redis"),
        redis_port=int(os.getenv("REDIS_PORT", "6379")),
        redis_password=os.getenv("REDIS_PASSWORD"),
    )

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_env: str = "local"
    log_level: str = "INFO"
    database_url: str = "sqlite+pysqlite:///./hse_delivery.db"
    azure_storage_connection_string: str = Field(default="UseDevelopmentStorage=true")
    azure_storage_container_name: str = "delivery-documents"
    max_upload_size_mb: int = 10
    cors_allowed_origins: str = ""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    @property
    def cors_origins(self) -> list[str]:
        if not self.cors_allowed_origins:
            return []
        return [origin.strip() for origin in self.cors_allowed_origins.split(",") if origin.strip()]


settings = Settings()

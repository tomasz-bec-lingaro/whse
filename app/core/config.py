from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_env: str = "local"
    log_level: str = "INFO"
    database_url: str = "sqlite+pysqlite:///./whse_delivery.db"
    azure_storage_connection_string: str = Field(default="UseDevelopmentStorage=true")
    azure_storage_container_name: str = "delivery-documents"
    max_upload_size_mb: int = 10
    upload_rate_limit_per_minute: int = 30
    upload_rate_limit_window_seconds: int = 60
    cors_allowed_origins: str = ""
    api_key: str = "local-dev-api-key"
    api_key_roles: str = "whs:operator"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    @property
    def cors_origins(self) -> list[str]:
        if not self.cors_allowed_origins:
            return []
        return [origin.strip() for origin in self.cors_allowed_origins.split(",") if origin.strip()]

    @property
    def api_roles(self) -> frozenset[str]:
        return frozenset(role.strip() for role in self.api_key_roles.split(",") if role.strip())


settings = Settings()

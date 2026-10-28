"""Application configuration management using Pydantic Settings."""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Anthropic API
    anthropic_api_key: str

    # Database
    database_url: str

    # Application
    environment: str = "development"
    log_level: str = "INFO"
    log_format: str = "json"

    # Server
    api_port: int = 8000
    api_host: str = "0.0.0.0"
    mcp_port: int = 8001

    # Streamlit
    streamlit_port: int = 8501
    streamlit_client_logger_level: str = "info"

    # Database Pool
    db_pool_size: int = 10
    db_max_overflow: int = 20

    # API
    api_timeout: int = 60
    max_workers: int = 10

    # Feature Flags
    enable_mcp_logging: bool = True
    enable_audit_trail: bool = True
    enable_mock_data: bool = True

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


# Global settings instance
settings = Settings()

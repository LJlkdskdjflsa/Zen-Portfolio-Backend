import os

from pydantic_settings import BaseSettings


def get_secret_manager_or_none(env_var: str) -> str | None:
    return None


class Settings(BaseSettings):
    """Application settings.

    Attributes:
        privy_app_id: Privy application ID for authentication
        privy_app_secret: Privy application secret for authentication
        helius_api_key: Helius RPC API key for Solana network access
        codex_api_key: Codex GraphQL API key for token price data
    """
    
    # DB
    POSTGRES_USER: str = get_secret_manager_or_none("user_service_database_execution_agents_username")
    POSTGRES_PASSWORD: str = get_secret_manager_or_none("user_service_database_execution_agents_password")
    POSTGRES_SERVER: str = get_secret_manager_or_none("user_database_server")
    POSTGRES_PORT: int = 5432
    POSTGRES_DB: str = "zen-portfolio"

    # redis Settings
    REDIS_HOST: str = get_secret_manager_or_none("data_redis_host")
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    REDIS_PASSWORD: str | None = None

    # OpenAI
    OPENAI_API_KEY: str = get_secret_manager_or_none("openai_api_key")

    # Solana Tracker
    SOLANA_TRACKER_API_KEY: str = get_secret_manager_or_none("solana_tracker_api_key")

    # Moralis
    MORALIS_API_KEY: str = get_secret_manager_or_none("moralis_api_key")

    # Helius
    HELIUS_API_KEY: str = get_secret_manager_or_none("helius_api_key")
    
    model_config = {
        "env_file": ".env" + "." + os.environ.get("ACTIVE_PROFILE", "local"),
        "extra": "ignore",
    }

    @property
    def POSTGRES_URL(self):
        return (
            f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@"
            f"{self.POSTGRES_SERVER}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )


settings = Settings()

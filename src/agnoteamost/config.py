"""Configuration management for AgnoTeam."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # LLM Configuration
    openai_api_key: str | None = None
    anthropic_api_key: str | None = None
    google_api_key: str | None = None  # Gemini API key
    default_model: str = "gemini-2.5-flash"
    specialist_model: str = "gemini-2.5-pro"

    # Mattermost Configuration
    mattermost_url: str = "http://localhost:8065"
    mattermost_token: str = ""
    mattermost_team: str = "main"
    mattermost_bot_name: str = "executive-bot"
    mattermost_bot_id: str = ""  # Bot user ID for mention detection
    mattermost_reply_to_mentions_only: bool = True

    # Mem0 Cloud Configuration
    mem0_api_key: str | None = None  # Mem0 cloud API key
    mem0_project_id: str | None = None  # Mem0 project ID
    # Legacy self-hosted settings (fallback)
    mem0_provider: str = "openai"
    mem0_vector_store: str = "qdrant"
    mem0_vector_store_url: str = "http://localhost:6333"
    mem0_collection_name: str = "agnoteam_memories"

    # ERPNext MCP Configuration
    erpnext_projects_mcp_url: str = "https://9547--main--megaspace--jxu002700.xuperson.org/mcp"
    erpnext_crm_mcp_url: str = "https://9557--main--megaspace--jxu002700.xuperson.org/mcp"

    # Gitea MCP Configuration
    gitea_mcp_url: str = "https://8765--main--megaspace--jxu002700.xuperson.org/mcp"

    # Database Configuration (for AgentOS persistence)
    database_url: str = "sqlite:///agnoteam.db"

    # Server Configuration
    host: str = "0.0.0.0"
    port: int = 8000
    debug: bool = False

    @property
    def use_mem0_cloud(self) -> bool:
        """Check if Mem0 cloud should be used."""
        return bool(self.mem0_api_key)

    @property
    def use_gemini(self) -> bool:
        """Check if Gemini should be used as LLM provider."""
        return bool(self.google_api_key) and "gemini" in self.default_model.lower()


settings = Settings()

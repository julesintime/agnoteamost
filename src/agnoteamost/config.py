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
    default_model: str = "gpt-4o"
    specialist_model: str = "gpt-4o-mini"

    # Mattermost Configuration
    mattermost_url: str = "http://localhost:8065"
    mattermost_token: str = ""
    mattermost_team: str = "main"
    mattermost_bot_name: str = "executive-bot"
    mattermost_reply_to_mentions_only: bool = True

    # Mem0 Configuration
    mem0_provider: str = "openai"  # openai, anthropic, ollama
    mem0_vector_store: str = "qdrant"  # qdrant, chroma, pinecone
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


settings = Settings()

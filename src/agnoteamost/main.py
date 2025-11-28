"""Main entry point for AgnoTeam - Corporate Executive Team Agents.

Starts the AgentOS server with:
- Mattermost interface for chat interaction
- Executive team (CEO, CFO, COO, CTO)
- Mem0 memory integration
- ERPNext and Gitea MCP tool integration
"""

from __future__ import annotations

import asyncio
import logging
import os
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI

from agnoteamost.config import settings
from agnoteamost.agents.executive_team import create_executive_team
from agnoteamost.interfaces.mattermost import Mattermost
from agnoteamost.interfaces.mattermost.mattermost import MattermostConfig
from agnoteamost.tools.erpnext_tools import (
    create_erpnext_crm_tools,
    create_erpnext_projects_tools,
)
from agnoteamost.tools.gitea_tools import create_gitea_tools

# Configure logging
logging.basicConfig(
    level=logging.DEBUG if settings.debug else logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def create_app() -> FastAPI:
    """Create and configure the FastAPI application.

    Returns:
        Configured FastAPI app with AgentOS integration
    """
    # Initialize MCP tools
    logger.info("Initializing MCP tools...")

    try:
        cfo_tools = [create_erpnext_crm_tools()]
        logger.info("ERPNext CRM tools initialized")
    except Exception as e:
        logger.warning(f"Failed to initialize ERPNext CRM tools: {e}")
        cfo_tools = []

    try:
        coo_gitea_tools = create_gitea_tools()
        coo_erpnext_tools = create_erpnext_projects_tools()
        coo_tools = [coo_gitea_tools, coo_erpnext_tools]
        logger.info("COO tools initialized (Gitea + ERPNext Projects)")
    except Exception as e:
        logger.warning(f"Failed to initialize COO tools: {e}")
        coo_tools = []

    try:
        cto_tools = [create_gitea_tools()]
        logger.info("Gitea tools initialized for CTO")
    except Exception as e:
        logger.warning(f"Failed to initialize Gitea tools: {e}")
        cto_tools = []

    # Create executive team
    logger.info("Creating executive team...")
    executive_team = create_executive_team(
        cfo_tools=cfo_tools,
        coo_tools=coo_tools,
        cto_tools=cto_tools,
    )
    logger.info(f"Executive team created with {len(executive_team.members)} members")

    # Create Mattermost interface
    mattermost_config = MattermostConfig(
        url=settings.mattermost_url,
        token=settings.mattermost_token,
        team=settings.mattermost_team,
        bot_name=settings.mattermost_bot_name,
        bot_id=settings.mattermost_bot_id,
        reply_to_mentions_only=settings.mattermost_reply_to_mentions_only,
    )

    mattermost_interface = Mattermost(
        team=executive_team,
        config=mattermost_config,
    )

    # Create FastAPI app with lifespan
    @asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
        """Manage application lifespan."""
        logger.info("Starting AgnoTeam server...")

        # Start Mattermost WebSocket listener in background
        if settings.mattermost_token:
            asyncio.create_task(mattermost_interface.start_websocket_listener())
            logger.info("Mattermost WebSocket listener started")
        else:
            logger.warning("Mattermost token not configured, WebSocket disabled")

        yield

        # Cleanup
        logger.info("Shutting down AgnoTeam server...")
        await mattermost_interface.disconnect()

    app = FastAPI(
        title="AgnoTeam - Corporate Executive Team Agents",
        description="Multi-agent system with Mattermost interface, Mem0 memory, and ERPNext integration",
        version="0.1.0",
        lifespan=lifespan,
    )

    # Attach Mattermost routes
    mattermost_interface.attach_routes(app)

    # Health check endpoint
    @app.get("/health")
    async def health() -> dict[str, str]:
        return {
            "status": "healthy",
            "service": "agnoteam",
            "team_members": str(len(executive_team.members)),
        }

    # Root endpoint
    @app.get("/")
    async def root() -> dict[str, str]:
        return {
            "message": "AgnoTeam - Corporate Executive Team Agents",
            "docs": "/docs",
            "health": "/health",
            "mattermost_webhook": "/mattermost/webhook",
            "mattermost_command": "/mattermost/command",
        }

    return app


# Create app instance
app = create_app()


def main() -> None:
    """Run the server using uvicorn."""
    import uvicorn

    uvicorn.run(
        "agnoteamost.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
    )


if __name__ == "__main__":
    main()

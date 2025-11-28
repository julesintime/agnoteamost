"""Main entry point for AgnoTeam - Corporate Executive Team Agents.

Starts the AgentOS server with:
- AgentOS UI enabled
- Mattermost interface for chat interaction
- Executive team (CEO, CFO, COO, CTO)
- Mem0 memory integration
- ERPNext and Gitea MCP tool integration
"""

from __future__ import annotations

import logging

from agno.os import AgentOS
from agno.db.postgres import PostgresDb

from agnoteamost.config import settings
from agnoteamost.agents.executive_team import create_executive_team
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

# Create AgentOS with team
# AgentOS UI is automatically enabled at /ui
agent_os = AgentOS(
    name="AgnoTeam",
    description="Corporate Executive Team with CEO, CFO, COO, CTO",
    version="0.1.0",
    teams=[executive_team],
)

# Get the FastAPI app from AgentOS
app = agent_os.get_app()

logger.info("AgentOS initialized - UI available at /ui")


def main() -> None:
    """Run the server using AgentOS serve."""
    agent_os.serve(
        app="agnoteamost.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
    )


if __name__ == "__main__":
    main()

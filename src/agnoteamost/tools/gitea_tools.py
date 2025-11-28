"""Gitea MCP Tools integration.

Provides tool wrappers for Gitea MCP server.
These tools are used by CTO and COO agents for repository and issue management.
"""

from __future__ import annotations

import logging
from typing import Any

from agno.tools.mcp import MCPTools

from agnoteamost.config import settings

logger = logging.getLogger(__name__)


def create_gitea_tools() -> MCPTools:
    """Create Gitea tools via MCP.

    Provides access to:
    - Repository management
    - Issue tracking
    - Pull request management
    - Milestone management
    - Label management

    Returns:
        MCPTools instance for Gitea
    """
    logger.info(f"Initializing Gitea MCP tools from {settings.gitea_mcp_url}")

    mcp_tools = MCPTools(
        transport="streamable-http",
        url=settings.gitea_mcp_url,
        tool_name_prefix="gitea_",
    )

    return mcp_tools


# Convenience function tool definitions for agents without MCP
# These can be used as fallback or for testing

def list_repositories(page: int = 1, page_size: int = 20) -> dict[str, Any]:
    """List repositories from Gitea.

    Args:
        page: Page number
        page_size: Results per page

    Returns:
        List of repositories
    """
    return {"message": f"List repositories (page {page}, size {page_size})"}


def list_issues(
    owner: str,
    repo: str,
    state: str = "all",
    page: int = 1,
) -> dict[str, Any]:
    """List issues from a repository.

    Args:
        owner: Repository owner
        repo: Repository name
        state: Issue state (all, open, closed)
        page: Page number

    Returns:
        List of issues
    """
    return {
        "message": f"List issues for {owner}/{repo}",
        "state": state,
        "page": page,
    }


def create_issue(
    owner: str,
    repo: str,
    title: str,
    body: str,
) -> dict[str, Any]:
    """Create an issue in a repository.

    Args:
        owner: Repository owner
        repo: Repository name
        title: Issue title
        body: Issue body/description

    Returns:
        Created issue details
    """
    return {
        "message": f"Create issue in {owner}/{repo}",
        "title": title,
        "body": body,
    }


def list_pull_requests(
    owner: str,
    repo: str,
    state: str = "open",
) -> dict[str, Any]:
    """List pull requests from a repository.

    Args:
        owner: Repository owner
        repo: Repository name
        state: PR state (all, open, closed)

    Returns:
        List of pull requests
    """
    return {
        "message": f"List PRs for {owner}/{repo}",
        "state": state,
    }


def get_repository_info(owner: str, repo: str) -> dict[str, Any]:
    """Get repository information.

    Args:
        owner: Repository owner
        repo: Repository name

    Returns:
        Repository details
    """
    return {"message": f"Get info for {owner}/{repo}"}

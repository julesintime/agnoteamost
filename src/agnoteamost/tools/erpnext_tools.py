"""ERPNext MCP Tools integration.

Provides tool wrappers for ERPNext CRM and Projects MCP servers.
These tools are used by CFO (CRM) and COO (Projects) agents.
"""

from __future__ import annotations

import logging
from typing import Any

from agno.tools.mcp import MCPTools

from agnoteamost.config import settings

logger = logging.getLogger(__name__)


def create_erpnext_crm_tools() -> MCPTools:
    """Create ERPNext CRM tools via MCP.

    Provides access to:
    - Customer management
    - Lead management
    - Quotations
    - Sales Orders
    - Invoices

    Returns:
        MCPTools instance for ERPNext CRM
    """
    logger.info(f"Initializing ERPNext CRM MCP tools from {settings.erpnext_crm_mcp_url}")

    mcp_tools = MCPTools(
        transport="sse",
        url=settings.erpnext_crm_mcp_url,
        tool_name_prefix="erpnext_crm_",
    )

    return mcp_tools


def create_erpnext_projects_tools() -> MCPTools:
    """Create ERPNext Projects tools via MCP.

    Provides access to:
    - Project management
    - Task tracking
    - Timesheet management
    - Employee management
    - Attendance tracking

    Returns:
        MCPTools instance for ERPNext Projects
    """
    logger.info(f"Initializing ERPNext Projects MCP tools from {settings.erpnext_projects_mcp_url}")

    mcp_tools = MCPTools(
        transport="sse",
        url=settings.erpnext_projects_mcp_url,
        tool_name_prefix="erpnext_projects_",
    )

    return mcp_tools


# Convenience function tool definitions for agents without MCP
# These can be used as fallback or for testing

def search_customers(query: str, limit: int = 10) -> dict[str, Any]:
    """Search for customers in ERPNext.

    Args:
        query: Search query
        limit: Maximum results

    Returns:
        Search results
    """
    # This would be replaced by MCP tool call in production
    return {"message": f"Search customers for '{query}' (limit: {limit})"}


def create_quotation(
    customer: str,
    items: list[dict[str, Any]],
    valid_till: str | None = None,
) -> dict[str, Any]:
    """Create a quotation in ERPNext.

    Args:
        customer: Customer name
        items: List of items with qty and rate
        valid_till: Validity date

    Returns:
        Created quotation details
    """
    return {
        "message": f"Create quotation for {customer}",
        "items": items,
        "valid_till": valid_till,
    }


def get_project_status(project_name: str) -> dict[str, Any]:
    """Get status of a project from ERPNext.

    Args:
        project_name: Name of the project

    Returns:
        Project status details
    """
    return {"message": f"Get status for project '{project_name}'"}


def list_employees(status: str = "Active") -> dict[str, Any]:
    """List employees from ERPNext.

    Args:
        status: Employee status filter

    Returns:
        List of employees
    """
    return {"message": f"List employees with status '{status}'"}

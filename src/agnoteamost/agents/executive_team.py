"""Executive Team - Multi-Agent Coordination.

Creates and coordinates the executive team with CEO as leader
and CFO, COO, CTO as specialist members.
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from agno.team import Team

from agnoteamost.config import settings
from agnoteamost.agents.ceo import create_ceo_agent, get_model
from agnoteamost.agents.cfo import create_cfo_agent
from agnoteamost.agents.coo import create_coo_agent
from agnoteamost.agents.cto import create_cto_agent

if TYPE_CHECKING:
    from agno.tools.function import Function

logger = logging.getLogger(__name__)


TEAM_INSTRUCTIONS = """
You are the Executive Team of a corporate organization, led by the CEO.

## Team Structure
- **CEO (Leader)**: Strategic decisions, team coordination, final authority
- **CFO**: Financial analysis, budgeting, ROI calculations
- **COO**: Operations, project management, resource allocation
- **CTO**: Technology strategy, architecture, development oversight

## Delegation Guidelines

### When to involve CFO:
- Budget and cost questions
- Revenue and profitability discussions
- Investment decisions
- Financial reporting
- Quotations and invoicing

### When to involve COO:
- Project status and timelines
- Resource allocation
- Process improvements
- Team capacity
- Operational blockers

### When to involve CTO:
- Technical architecture decisions
- Code reviews and pull requests
- Technology evaluations
- Development estimates
- Security concerns

## Team Coordination
1. For complex decisions, gather input from relevant executives
2. Each executive provides their domain expertise
3. CEO synthesizes inputs and makes final decision
4. Document decisions and rationale

## Response Format
When multiple executives contribute:
1. Clearly attribute each perspective
2. Highlight agreements and disagreements
3. Provide a unified recommendation
4. Include action items with owners

## Memory Integration
The team shares organizational memory:
- Past decisions are available for reference
- Customer interactions are tracked
- Project history informs planning
- Technical decisions are documented
"""


def create_executive_team(
    cfo_tools: list[Function] | None = None,
    coo_tools: list[Function] | None = None,
    cto_tools: list[Function] | None = None,
    model_id: str | None = None,
) -> Team:
    """Create the executive team.

    Args:
        cfo_tools: Tools for CFO (ERPNext CRM)
        coo_tools: Tools for COO (ERPNext Projects + Gitea)
        cto_tools: Tools for CTO (Gitea)
        model_id: LLM model for team leader

    Returns:
        Configured executive team
    """
    # Create specialist agents
    cfo = create_cfo_agent(tools=cfo_tools)
    coo = create_coo_agent(tools=coo_tools)
    cto = create_cto_agent(tools=cto_tools)

    # Get team leader model (uses default_model which is Gemini)
    model = get_model(model_id, is_leader=True)

    team = Team(
        name="Executive Team",
        model=model,
        members=[cfo, coo, cto],
        instructions=TEAM_INSTRUCTIONS,
        share_member_interactions=True,
        add_team_history_to_members=True,
        show_members_responses=True,
        markdown=True,
    )

    return team

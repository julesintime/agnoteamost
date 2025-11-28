"""COO Agent - Operations and Project Management.

The COO agent handles operational matters including project management,
resource allocation, and process optimization.
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from agno.agent import Agent

from agnoteamost.config import settings
from agnoteamost.agents.ceo import get_model
from agnoteamost.memory.mem0_manager import memory_manager

if TYPE_CHECKING:
    from agno.tools.function import Function

logger = logging.getLogger(__name__)


COO_INSTRUCTIONS = """
You are the COO (Chief Operating Officer) of a corporate organization. Your role is to:

1. **Operations Management**: Oversee daily operations and processes
2. **Project Management**: Manage projects, timelines, and deliverables
3. **Resource Allocation**: Optimize team capacity and assignments
4. **Process Optimization**: Improve operational efficiency
5. **Team Coordination**: Coordinate cross-functional teams
6. **Risk Management**: Identify and mitigate operational risks

## Core Responsibilities
- Ensure projects are delivered on time and within budget
- Manage team workload and capacity
- Resolve operational blockers and conflicts
- Implement and improve business processes
- Track KPIs and operational metrics

## Tools Available
You have access to:
- ERPNext Projects: Tasks, timesheets, project tracking
- Gitea: Issues, milestones, sprint management
- Use these tools to track and manage work

## Communication Style
- Focus on actionable items and timelines
- Provide clear status updates (on-track, at-risk, blocked)
- Identify dependencies and blockers
- Use project management terminology

## Decision Framework
1. Assess resource availability and capacity
2. Evaluate dependencies and critical path
3. Identify risks and mitigation strategies
4. Consider impact on other projects/teams
5. Provide realistic timelines with confidence levels

## Sprint/Project Tracking
When asked about project status:
1. Query Gitea for issue status
2. Summarize: completed, in-progress, blocked
3. Calculate completion percentage
4. Highlight risks and blockers
5. Recommend next steps

## Memory Usage
Use organizational memory to:
- Track project history and lessons learned
- Remember team capacity and skills
- Reference past operational decisions
- Maintain process documentation
"""


def create_coo_agent(
    tools: list[Function] | None = None,
    model_id: str | None = None,
) -> Agent:
    """Create the COO agent.

    Args:
        tools: Additional tools (ERPNext Projects + Gitea tools)
        model_id: LLM model ID (defaults to specialist model)

    Returns:
        Configured COO agent
    """
    model = get_model(model_id, is_leader=False)

    agent = Agent(
        name="COO",
        model=model,
        role="Chief Operating Officer - Operations & Project Management",
        instructions=COO_INSTRUCTIONS,
        tools=tools or [],
        add_history_to_messages=True,
        num_history_responses=3,
        markdown=True,
        show_tool_calls=True,
    )

    return agent

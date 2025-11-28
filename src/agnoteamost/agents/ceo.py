"""CEO Agent - Strategic Leadership and Decision Making.

The CEO agent serves as the team leader, coordinating other executives
and making strategic decisions. It synthesizes input from CFO, COO, and CTO.
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any

from agno.agent import Agent

from agnoteamost.config import settings
from agnoteamost.memory.mem0_manager import memory_manager

if TYPE_CHECKING:
    from agno.tools.function import Function

logger = logging.getLogger(__name__)


CEO_INSTRUCTIONS = """
You are the CEO of a corporate organization. Your role is to:

1. **Strategic Leadership**: Make high-level strategic decisions that affect the entire organization
2. **Team Coordination**: Coordinate with CFO (Finance), COO (Operations), and CTO (Technology)
3. **Vision Setting**: Maintain and communicate the company's vision and goals
4. **Stakeholder Management**: Balance interests of employees, customers, and shareholders
5. **Decision Making**: Make final decisions when executives have conflicting recommendations

## Communication Style
- Be decisive but considerate of all perspectives
- Summarize key points from each executive's input
- Provide clear direction and next steps
- Use business terminology appropriately

## When Delegating
- Financial matters: Ask CFO for analysis
- Operational matters: Ask COO for implementation plans
- Technical matters: Ask CTO for feasibility assessment

## Decision Framework
1. Gather input from relevant executives
2. Consider financial impact (CFO perspective)
3. Consider operational feasibility (COO perspective)
4. Consider technical requirements (CTO perspective)
5. Balance short-term and long-term goals
6. Make a clear decision with rationale

## Memory Usage
You have access to organizational memory. Use it to:
- Reference past decisions and their outcomes
- Maintain consistency in strategic direction
- Learn from previous discussions
"""


def get_model(model_id: str | None = None, is_leader: bool = True) -> Any:
    """Get the appropriate model based on configuration.

    Args:
        model_id: Optional model ID override
        is_leader: Whether this is a team leader (uses default_model) or specialist

    Returns:
        Configured model instance
    """
    model_name = model_id or (settings.default_model if is_leader else settings.specialist_model)

    if settings.use_gemini or "gemini" in model_name.lower():
        from agno.models.google import Gemini
        return Gemini(
            id=model_name,
            api_key=settings.google_api_key,
        )
    else:
        from agno.models.openai import OpenAIChat
        return OpenAIChat(
            id=model_name,
            api_key=settings.openai_api_key,
        )


def create_ceo_agent(
    tools: list[Function] | None = None,
    model_id: str | None = None,
) -> Agent:
    """Create the CEO agent.

    Args:
        tools: Additional tools for the agent
        model_id: LLM model ID (defaults to settings)

    Returns:
        Configured CEO agent
    """
    model = get_model(model_id, is_leader=True)

    agent = Agent(
        name="CEO",
        model=model,
        role="Chief Executive Officer - Strategic Leadership",
        instructions=CEO_INSTRUCTIONS,
        tools=tools or [],
        add_history_to_messages=True,
        num_history_responses=5,
        markdown=True,
        show_tool_calls=True,
    )

    return agent

"""CFO Agent - Financial Analysis and Budget Management.

The CFO agent handles all financial matters including budgeting,
forecasting, financial reporting, and ROI analysis.
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


CFO_INSTRUCTIONS = """
You are the CFO (Chief Financial Officer) of a corporate organization. Your role is to:

1. **Financial Analysis**: Analyze financial data, trends, and metrics
2. **Budget Management**: Create, monitor, and adjust budgets
3. **Forecasting**: Develop financial forecasts and projections
4. **Cost Optimization**: Identify opportunities to reduce costs
5. **Investment Decisions**: Evaluate ROI and make investment recommendations
6. **Compliance**: Ensure financial compliance and reporting standards

## Core Responsibilities
- Review and approve major expenditures
- Provide financial impact analysis for strategic decisions
- Monitor cash flow and liquidity
- Manage relationships with banks and investors
- Oversee accounting and financial reporting

## Tools Available
You have access to ERPNext CRM tools for:
- Creating and managing quotations
- Tracking invoices and payments
- Managing customer financial records
- Generating financial reports

## Communication Style
- Use precise numbers and percentages
- Provide clear cost-benefit analysis
- Highlight financial risks and opportunities
- Reference historical financial data when relevant

## Decision Framework
1. Analyze financial impact (revenue, costs, margins)
2. Calculate ROI and payback period
3. Assess risk level and mitigation strategies
4. Consider cash flow implications
5. Provide recommendation with supporting data

## Memory Usage
Use organizational memory to:
- Reference past financial decisions
- Track budget history and variances
- Remember customer financial interactions
- Maintain consistency in financial policies
"""


def create_cfo_agent(
    tools: list[Function] | None = None,
    model_id: str | None = None,
) -> Agent:
    """Create the CFO agent.

    Args:
        tools: Additional tools for the agent (typically ERPNext CRM tools)
        model_id: LLM model ID (defaults to specialist model)

    Returns:
        Configured CFO agent
    """
    model = get_model(model_id, is_leader=False)

    agent = Agent(
        name="CFO",
        model=model,
        role="Chief Financial Officer - Financial Analysis & Budget",
        instructions=CFO_INSTRUCTIONS,
        tools=tools or [],
        add_history_to_context=True,
        num_history_messages=3,
        markdown=True,
    )

    return agent

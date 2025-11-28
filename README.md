# AgnoTeam: Corporate Executive Team Agents

An Agno/AgentOS-based multi-agent system for corporate executive team simulation with:
- **Mattermost Interface** - Chat-based interaction via Mattermost
- **Mem0 Memory Support** - Persistent, self-improving memory for agents
- **ERPNext Integration** - CRM and project management via MCP tools
- **Gitea Integration** - Issue and repository management via MCP tools

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                         Mattermost Interface                         │
│                    (WebSocket + REST API Events)                     │
└─────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────┐
│                           AgentOS Runtime                            │
│  ┌───────────────────────────────────────────────────────────────┐  │
│  │                    Executive Team (Leader)                      │  │
│  │                         CEO Agent                              │  │
│  └───────────────────────────────────────────────────────────────┘  │
│                                    │                                 │
│           ┌────────────────────────┼────────────────────────┐       │
│           ▼                        ▼                        ▼       │
│  ┌────────────────┐    ┌────────────────┐    ┌────────────────┐    │
│  │   CFO Agent    │    │   COO Agent    │    │   CTO Agent    │    │
│  │  (Finance)     │    │  (Operations)  │    │  (Technology)  │    │
│  └────────────────┘    └────────────────┘    └────────────────┘    │
│           │                        │                        │       │
│           └────────────────────────┼────────────────────────┘       │
│                                    │                                 │
│  ┌───────────────────────────────────────────────────────────────┐  │
│  │                      Mem0 Memory Layer                         │  │
│  │           (Persistent memories across sessions)                │  │
│  └───────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────┘
                                    │
                    ┌───────────────┼───────────────┐
                    ▼               ▼               ▼
            ┌─────────────┐ ┌─────────────┐ ┌─────────────┐
            │   ERPNext   │ │    Gitea    │ │   Other     │
            │   MCP Tools │ │  MCP Tools  │ │   Tools     │
            └─────────────┘ └─────────────┘ └─────────────┘
```

## Executive Team Agents

### CEO Agent (Team Leader)
- **Role**: Strategic decision-making, team coordination
- **Capabilities**: Synthesizes input from all executives, makes final decisions
- **Memory**: Company vision, strategic goals, key decisions

### CFO Agent (Finance)
- **Role**: Financial analysis, budget management, forecasting
- **Tools**: ERPNext CRM (quotations, invoices, payments)
- **Memory**: Financial metrics, budget constraints, cost history

### COO Agent (Operations)
- **Role**: Project management, resource allocation, process optimization
- **Tools**: ERPNext Projects (tasks, timesheets), Gitea (issues, milestones)
- **Memory**: Project status, team capacity, operational processes

### CTO Agent (Technology)
- **Role**: Technical architecture, development oversight, tech strategy
- **Tools**: Gitea (repositories, pull requests, code reviews)
- **Memory**: Technical decisions, architecture patterns, tech debt

## Features

- **Multi-Agent Collaboration**: Agents share context and delegate tasks
- **Persistent Memory**: Mem0 provides long-term memory across sessions
- **Real-time Chat**: Mattermost integration for team communication
- **ERP Integration**: ERPNext for business operations (CRM, HR, Projects)
- **Git Integration**: Gitea for development workflow management
- **Event Streaming**: Real-time visibility into agent execution

## Installation

```bash
# Clone the repository
git clone https://git.xuperson.org/joe/agnoteamost.git
cd agnoteamost

# Install dependencies
pip install -e ".[dev]"

# Configure environment
cp .env.example .env
# Edit .env with your credentials
```

## Configuration

### Required Environment Variables

```bash
# LLM Provider (OpenAI or Anthropic)
OPENAI_API_KEY=sk-...
# or
ANTHROPIC_API_KEY=sk-ant-...

# Mattermost
MATTERMOST_URL=https://mattermost.example.com
MATTERMOST_TOKEN=your-bot-token
MATTERMOST_TEAM=your-team-name

# Mem0 (OpenSource mode)
MEM0_VECTOR_STORE_URL=http://localhost:6333

# ERPNext MCP
ERPNEXT_MCP_URL=https://your-erpnext-mcp.com/mcp

# Gitea MCP
GITEA_MCP_URL=https://your-gitea-mcp.com/mcp
```

## Usage

### Start the AgentOS Server

```bash
# Development mode
python -m agnoteamost.main

# Production mode
uvicorn agnoteamost.main:app --host 0.0.0.0 --port 8000
```

### Interact via Mattermost

1. Add the bot to your Mattermost team
2. Mention the bot or send a direct message
3. Ask questions or request actions

**Example interactions:**

```
@executive-bot What's our Q4 financial outlook?
@executive-bot Create a project plan for the new product launch
@executive-bot Review the open issues in our main repository
@executive-bot Schedule a meeting with the engineering team
```

## Project Structure

```
agnoteamost/
├── src/
│   └── agnoteamost/
│       ├── __init__.py
│       ├── main.py                 # AgentOS entry point
│       ├── config.py               # Configuration management
│       ├── interfaces/
│       │   ├── __init__.py
│       │   └── mattermost/         # Mattermost interface
│       │       ├── __init__.py
│       │       ├── mattermost.py   # Main interface class
│       │       ├── router.py       # FastAPI routes
│       │       └── security.py     # Token validation
│       ├── agents/
│       │   ├── __init__.py
│       │   ├── executive_team.py   # Executive team definition
│       │   ├── ceo.py              # CEO agent
│       │   ├── cfo.py              # CFO agent
│       │   ├── coo.py              # COO agent
│       │   └── cto.py              # CTO agent
│       ├── memory/
│       │   ├── __init__.py
│       │   └── mem0_manager.py     # Mem0 integration
│       └── tools/
│           ├── __init__.py
│           ├── erpnext_tools.py    # ERPNext MCP tools
│           └── gitea_tools.py      # Gitea MCP tools
├── tests/
│   └── ...
├── pyproject.toml
├── .env.example
└── README.md
```

## Development

### Running Tests

```bash
pytest tests/
```

### Code Quality

```bash
# Format code
ruff format .

# Lint code
ruff check .

# Type check
mypy src/
```

## License

MIT License

## References

- [Agno Documentation](https://docs.agno.com)
- [Mem0 Documentation](https://docs.mem0.ai)
- [Mattermost API](https://api.mattermost.com)
- [ERPNext Documentation](https://docs.erpnext.com)
- [Gitea API](https://docs.gitea.com/api)

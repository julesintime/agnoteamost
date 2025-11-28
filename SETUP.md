# AgnoTeam Setup Guide

## ✅ What's Working

- **AgentOS Runtime**: Multi-agent system running on FastAPI
- **AgentOS UI**: Web interface at `/ui` for chatting with agents
- **Executive Team**: CEO (leader), CFO, COO, CTO with specialized roles
- **MCP Tools**: ERPNext CRM, ERPNext Projects, Gitea integration
- **Gemini Models**: Using gemini-2.5-flash (leader) and gemini-2.5-pro (specialists)
- **Mem0 Cloud**: Persistent memory across conversations

## 🚀 Quick Start

### 1. Activate Environment

```bash
source .venv/bin/activate
```

### 2. Start Server

```bash
agnoteamost
```

You'll see:

```
╔══════════════ AgentOS ═══════════════╗
║                                      ║
║         https://os.agno.com/         ║
║                                      ║
║  OS running on: http://0.0.0.0:8000  ║
╚══════════════════════════════════════╝
```

### 3. Access the UI

Open your browser and go to:

**http://localhost:8000/ui**

You can now chat with the Executive Team directly through the web interface!

## 🎯 Using the AgentOS UI

1. Navigate to **http://localhost:8000/ui**
2. Select **"Executive Team"** from the dropdown
3. Start chatting - the team will delegate to appropriate executives
4. Session history is automatically maintained

### Example Conversations

**Financial Query:**
```
"What's our Q4 revenue forecast?"
```
→ CEO delegates to CFO for financial analysis

**Project Status:**
```
"What's the status of the authentication feature?"
```
→ CEO delegates to COO for project tracking

**Technical Decision:**
```
"Should we use Redis or Memcached for caching?"
```
→ CEO delegates to CTO for technical evaluation

## 📡 API Endpoints

AgentOS provides standard REST API endpoints:

- **GET** `/` - API information
- **GET** `/ui` - Web interface
- **GET** `/teams` - List all teams
- **POST** `/teams/Executive Team/run` - Chat with team (programmatic)
- **GET** `/teams/Executive Team/sessions` - Session history
- **GET** `/health` - Health check

### API Example

```bash
curl -X POST http://localhost:8000/teams/Executive%20Team/run \
  -H "Content-Type: application/json" \
  -d '{"message": "What are our top priorities?"}'
```

## 🔧 Configuration

All settings are in `.env`:

### Required Settings

```env
# Gemini API
GOOGLE_API_KEY=your-gemini-api-key

# Mem0 Cloud
MEM0_API_KEY=your-mem0-api-key
MEM0_PROJECT_ID=your-project-id
```

### Optional Settings

```env
# Database (default: SQLite)
DATABASE_URL=sqlite:///agnoteam.db
# Or PostgreSQL for production:
# DATABASE_URL=postgresql://user:pass@host/db

# Server
HOST=0.0.0.0
PORT=8000
DEBUG=false
```

## 👥 Team Structure

### CEO (Team Leader)
- **Model**: gemini-2.5-flash
- **Role**: Strategic decisions, team coordination
- **Delegates to**: CFO, COO, CTO based on query

### CFO (Specialist)
- **Model**: gemini-2.5-pro
- **Role**: Financial analysis, budgeting, ROI
- **Tools**: ERPNext CRM (customers, quotations, invoices)

### COO (Specialist)
- **Model**: gemini-2.5-pro
- **Role**: Operations, project management
- **Tools**: ERPNext Projects, Gitea (issues, tasks)

### CTO (Specialist)
- **Model**: gemini-2.5-pro
- **Role**: Technology, architecture, code reviews
- **Tools**: Gitea (repos, PRs, branches)

## 🔌 MCP Tool Integration

The agents have access to:

### ERPNext CRM (CFO)
- Customer management
- Lead tracking
- Quotations and sales orders
- Invoice management

### ERPNext Projects (COO)
- Project tracking
- Task management
- Timesheet logging
- Employee management

### Gitea (COO, CTO)
- Repository management
- Issue tracking
- Pull request reviews
- Branch and release management

## 🧠 Memory & Knowledge

### Session Memory
- Conversations persist across requests
- Each team session maintains context
- Access previous discussions in the same session

### Mem0 Cloud Integration
- User preferences stored globally
- Project-specific memories
- Cross-session learning

## 📊 Monitoring

### Logs
```bash
# View logs while running
agnoteamost

# All INFO level logs show:
# - MCP tool initialization
# - Team member responses
# - Tool calls and results
```

### Health Check
```bash
curl http://localhost:8000/health
```

## 🐛 Troubleshooting

### MCP Tools Not Connecting

Check the MCP server URLs in `.env`:
```env
ERPNEXT_CRM_MCP_URL=https://your-erpnext-server/mcp
ERPNEXT_PROJECTS_MCP_URL=https://your-erpnext-server/mcp
GITEA_MCP_URL=https://your-gitea-server/mcp
```

### Agents Not Responding

1. Check Gemini API key is valid
2. Verify Mem0 cloud credentials
3. Check logs for errors

### UI Not Loading

1. Ensure server is running on port 8000
2. Check firewall settings
3. Try http://127.0.0.1:8000/ui

## 🚀 Production Deployment

### Use PostgreSQL

```env
DATABASE_URL=postgresql://user:pass@host:5432/agnoteam
```

### Docker Deployment

```bash
# Build image
docker build -t agnoteam .

# Run container
docker run -p 8000:8000 \
  -e GOOGLE_API_KEY=your-key \
  -e MEM0_API_KEY=your-key \
  -e MEM0_PROJECT_ID=your-project \
  agnoteam
```

### Environment Variables

All sensitive data should be in environment variables, never committed to git.

## 📚 Next Steps

1. **Explore the UI**: Chat with the team at http://localhost:8000/ui
2. **Test Delegation**: Ask questions that require different specialists
3. **Review Sessions**: Check conversation history in the UI
4. **Integrate Tools**: Connect your ERPNext and Gitea instances

## 🔗 Resources

- **AgentOS Docs**: https://docs.agno.com
- **Agno GitHub**: https://github.com/agno-agi/agno
- **Mem0 Docs**: https://docs.mem0.ai
- **ERPNext**: https://erpnext.com
- **Gitea**: https://gitea.io

---

**Note**: Mattermost webhook integration is available but requires additional setup. The AgentOS UI provides the easiest way to interact with the team.

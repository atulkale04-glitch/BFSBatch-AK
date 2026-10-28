# Loan Approval System - Multi-Agent Agentic AI

A production-ready multi-agent agentic AI system for automated loan approval that uses Claude LLM with LangGraph orchestration and MCP servers for specialized agent communication.

## 📋 Overview

This system automates loan application analysis and decision-making across multiple specialized AI agents:

- **Applicant Profile Agent** - Analyzes applicant information and employment history
- **Financial Risk Agent** - Calculates financial risk metrics and DTI ratios
- **Loan Decision Agent** - Synthesizes all evaluations to make final decisions
- **Compliance Orchestrator Agent** - Executes decisions and manages notifications

## 🏗️ Architecture

```
Streamlit UI
    ↓
FastAPI Microservice
    ↓
LangGraph Orchestrator
    ↓
[Agents] ←→ [MCP Servers]
    ↓
Decision → Notification → Database
```

## 🚀 Quick Start

### Prerequisites

- Python 3.9+
- PostgreSQL 12+ (optional for this phase)
- Anthropic API key

### Installation

1. **Clone and setup:**
   ```bash
   cd "/home/ubuntu/Desktop/Loan Approval System"
   source venv/bin/activate
   ```

2. **Configure environment:**
   ```bash
   cp .env.example .env
   # Edit .env with your settings
   ```

3. **Verify installation:**
   ```bash
   pip list | grep -E "fastapi|langgraph|anthropic"
   ```

### Running the Application

**Start FastAPI Server:**
```bash
source venv/bin/activate
uvicorn src.main:app --reload --port 8000
```

**API Documentation:**
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

**Health Check:**
```bash
curl http://localhost:8000/health
```

## 📁 Project Structure

```
/src
  ├── main.py                 # FastAPI application
  ├── api/
  │   └── routes.py          # API endpoints
  ├── models/
  │   ├── schemas.py         # Pydantic models
  │   ├── database.py        # SQLAlchemy ORM
  │   └── enums.py           # Enumerations
  ├── agents/                # Agent implementations (Phase 2)
  ├── mcp_servers/          # MCP server implementations (Phase 2)
  ├── orchestration/        # LangGraph workflows (Phase 3)
  ├── utils/                # Utilities
  └── database/             # Database management

/config
  ├── settings.py           # Configuration
  ├── thresholds.py         # Decision policies
  └── prompts.py            # Claude system prompts

/ui
  └── streamlit_app.py      # Streamlit UI (Phase 6)

/tests                       # Test suite

/docs                        # Documentation
```

## 📝 API Endpoints (Phase 1)

### Submit Loan Application
```http
POST /api/v1/applications
Content-Type: application/json

{
  "applicant_id": "APP-001",
  "age": 35,
  "income": 75000.0,
  "employment_type": "Full-time",
  "credit_score": 720,
  "loan_amount": 250000.0,
  "loan_tenure_months": 360,
  "existing_liabilities": 50000.0,
  "location": "New York"
}
```

### Get Application Status
```http
GET /api/v1/applications/{application_id}
```

### Get Decision
```http
GET /api/v1/applications/{application_id}/decision
```

### Health Check
```http
GET /health
```

## 🔧 Configuration

Edit `.env` file to configure:

```env
# API
ANTHROPIC_API_KEY=your_key_here
DATABASE_URL=postgresql://user:pass@localhost/loan_approval

# Server
ENVIRONMENT=development
LOG_LEVEL=DEBUG
API_PORT=8000

# Feature Flags
ENABLE_MCP_LOGGING=true
ENABLE_AUDIT_TRAIL=true
```

## 📊 Decision Thresholds

Located in `config/thresholds.py`:

- **Minimum Credit Score:** 650
- **Maximum DTI Ratio:** 0.45
- **Income Stability:** 70+
- **Auto-Approve Risk Score:** < 30
- **Auto-Reject Risk Score:** > 75
- **Manual Review:** 30-75 risk score

## 🧪 Testing

```bash
# Run all tests
pytest tests/

# Run specific test file
pytest tests/unit/test_validators.py

# Run with coverage
pytest --cov=src tests/
```

## 📚 Development Phases

- [x] **Phase 1** (Days 1-3): Foundation & Setup
  - [x] Project structure
  - [x] Python environment
  - [x] Database schema
  - [x] Configuration
  - [x] API skeleton

- [ ] **Phase 2** (Days 4-7): Infrastructure
  - [ ] MCP framework setup
  - [ ] Base agent class
  - [ ] MCP servers

- [ ] **Phase 3** (Days 8-10): Data Models
  - [ ] Database models
  - [ ] Pydantic schemas
  - [ ] FastAPI routes

- [ ] **Phase 4** (Days 11-17): Agents
  - [ ] Specialized agents
  - [ ] Claude integration
  - [ ] Agent testing

- [ ] **Phase 5** (Days 18-21): Orchestration
  - [ ] LangGraph workflow
  - [ ] Agent coordination
  - [ ] State management

- [ ] **Phase 6** (Days 22-24): API
  - [ ] Complete endpoints
  - [ ] Error handling
  - [ ] Logging

- [ ] **Phase 7** (Days 25-27): UI
  - [ ] Streamlit app
  - [ ] Forms
  - [ ] Dashboard

- [ ] **Phase 8** (Days 28-30): Testing & Deployment
  - [ ] Test suite
  - [ ] Documentation
  - [ ] Docker setup

## 📖 Documentation

- [Project Plan](./Projectplan.md) - Detailed implementation plan
- [Architecture](./docs/ARCHITECTURE.md) - System design (Phase 2)
- [API Reference](./docs/API.md) - Endpoint documentation (Phase 2)
- [Development Guide](./docs/DEVELOPMENT.md) - Setup and workflow (Phase 2)

## 🤝 Contributing

This is an educational project. See Projectplan.md for implementation guidelines.

## 📄 License

Educational project - 2024

## 📞 Support

For issues or questions, refer to:
- Projectplan.md for implementation details
- Config files for settings
- Utils for helper functions

---

**Status:** Phase 1 - Foundation Complete ✅

**Next Phase:** Phase 2 - MCP Servers & Agent Infrastructure

**Last Updated:** 2024-10-28

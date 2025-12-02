# Phoenix Digital Bank AI Agent 🏦

An intelligent banking assistant powered by LangGraph, FastAPI, and CopilotKit. This AI agent provides natural language banking operations including account management, money transfers, transaction history, and financial insights.

## ✨ Features

- **Natural Language Banking**: Interact with your bank accounts using conversational AI
- **Account Management**: View balances, account details, and manage multiple accounts
- **Money Transfers**: Transfer funds between accounts and to beneficiaries with approval workflow
- **Transaction History**: Query and analyze transaction history with intelligent filtering
- **Beneficiary Management**: Add, view, and manage transfer beneficiaries
- **Financial Insights**: Get spending analysis and account summaries
- **Multi-Provider LLM Support**: Works with OpenAI and SambaNova models
- **Observability**: Built-in Phoenix/Arize integration for monitoring and tracing

## 🏗️ Architecture

### Tech Stack

**Backend:**
- **FastAPI**: High-performance async API framework
- **LangGraph**: Agentic workflow orchestration
- **LangChain**: LLM integration and tooling
- **PostgreSQL**: Relational database for banking data
- **SQLAlchemy**: Async ORM for database operations
- **CopilotKit**: Agent runtime integration

**Frontend:**
- **Next.js 16**: React framework with App Router
- **CopilotKit React**: AI-powered chat interface
- **TypeScript**: Type-safe development
- **Tailwind CSS**: Utility-first styling
- **Recharts**: Data visualization

**Observability:**
- **Arize Phoenix**: LLM observability and tracing
- **OpenTelemetry**: Distributed tracing

## 📋 Prerequisites

- **Docker & Docker Compose** (recommended) OR:
  - Python 3.11+
  - Node.js 20+
  - PostgreSQL 16+
  - pnpm (for frontend)

- **API Keys** (at least one required):
  - OpenAI API key OR
  - SambaNova API key

## 🚀 Quick Start

### Option 1: Docker (Recommended)

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd bnk-agnt
   ```

2. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env and add your API keys
   ```

3. **Start all services**
   ```bash
   docker-compose up -d
   ```

4. **Access the application**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000/docs
   - Phoenix Observability: http://localhost:6006

### Option 2: Local Development

#### Backend Setup

1. **Navigate to backend directory**
   ```bash
   cd backend
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up PostgreSQL database**
   ```bash
   # Create database
   createdb banking_demo
   
   # Run initialization script
   psql banking_demo < ../database/init.sql
   ```

5. **Configure environment**
   ```bash
   cp ../.env.example ../.env
   # Edit .env with your database URL and API keys
   ```

6. **Start backend server**
   ```bash
   python main.py
   # Or: uvicorn main:app --reload
   ```

#### Frontend Setup

1. **Navigate to frontend directory**
   ```bash
   cd frontend
   ```

2. **Install dependencies**
   ```bash
   pnpm install
   ```

3. **Configure environment**
   ```bash
   cp .env.local.example .env.local
   # Edit if needed (defaults should work for local development)
   ```

4. **Start development server**
   ```bash
   pnpm dev
   ```

5. **Access the application**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000/docs

## ⚙️ Environment Variables

### Required Variables

```bash
# Database
DATABASE_URL=postgresql://USER:PASSWORD@HOST:5432/DATABASE

# LLM Provider (at least one required)
OPENAI_API_KEY=your_openai_api_key
SAMBANOVA_API_KEY=your_sambanova_api_key
```

### Optional Variables

```bash
# Model Configuration
DEFAULT_MODEL=gpt-4o
INTENT_CLASSIFIER_MODEL_PROVIDER=openai  # or sambanova

# Observability (Phoenix)
PHOENIX_COLLECTOR_ENDPOINT=http://localhost:6006/v1/traces
PHOENIX_PROJECT_NAME=bank-agent
PHOENIX_API_KEY=your_phoenix_api_key
PHOENIX_SPACE_ID=your_phoenix_space_id

# Transfer Limits
MAX_TRANSFER_AMOUNT=1000000

# Server Configuration
HOST=0.0.0.0
PORT=8000
```

## 📁 Project Structure

```
bnk-agnt/
├── backend/
│   ├── bankbot/           # LangGraph agent implementation
│   │   ├── graph.py       # Agent workflow graph
│   │   ├── nodes/         # Graph nodes (agent, intent, tools)
│   │   └── state.py       # Agent state management
│   ├── mcp/               # MCP tools and database layer
│   │   ├── mcp_impl.py    # Banking operations implementation
│   │   └── mcp_tool.py    # Tool definitions
│   ├── shared/            # Shared utilities
│   ├── config.py          # Configuration management
│   ├── main.py            # FastAPI application
│   └── requirements.txt   # Python dependencies
├── frontend/
│   ├── app/               # Next.js App Router
│   │   └── page.tsx       # Main chat interface
│   ├── components/        # React components
│   │   ├── AccountCard.tsx
│   │   ├── TransactionList.tsx
│   │   └── ...
│   └── package.json       # Node dependencies
├── database/
│   └── init.sql           # Database schema and seed data
├── docker-compose.yml     # Docker orchestration
└── .env.example           # Environment template
```

## 🎯 Usage

### Demo Users

The database is pre-seeded with three demo users:

1. **Alice Ahmed** (`a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11`)
   - Salary Account: AED 15,000
   - Savings Account: AED 40,000

2. **Bob Mansour** (`b0eebc99-9c0b-4ef8-bb6d-6bb9bd380b22`)
   - Main Account: AED 25,000
   - Savings Account: AED 60,000

3. **Carol Ali** (`c0eebc99-9c0b-4ef8-bb6d-6bb9bd380c33`)
   - Current Account: AED 18,000
   - Premium Savings: AED 100,000

### Example Interactions

- "Show me my account balances"
- "What were my transactions last week?"
- "Transfer 500 AED from my salary account to savings"
- "Show my pending transfers"
- "Who are my beneficiaries?"
- "Analyze my spending by category"

## 🔧 API Documentation

Once the backend is running, visit http://localhost:8000/docs for interactive API documentation (Swagger UI).

### Key Endpoints

- `POST /copilotkit` - Main CopilotKit agent endpoint
- `GET /health` - Health check endpoint

## 🧪 Development

### Running Tests

```bash
cd backend
pytest tests/
```

### Code Quality

```bash
# Backend linting
cd backend
pylint bankbot/ mcp/

# Frontend linting
cd frontend
pnpm lint
```

## 📊 Observability

The application includes built-in observability through Arize Phoenix:

1. **Start Phoenix** (included in docker-compose):
   ```bash
   docker-compose up phoenix
   ```

2. **Access Phoenix UI**: http://localhost:6006

3. **View traces**: All LLM calls, tool executions, and agent decisions are automatically traced

## 🐛 Troubleshooting

### Database Connection Issues

```bash
# Check if PostgreSQL is running
docker-compose ps postgres

# View database logs
docker-compose logs postgres

# Reset database
docker-compose down -v
docker-compose up -d postgres
```

### Frontend Build Errors

```bash
# Clear Next.js cache
cd frontend
rm -rf .next node_modules
pnpm install
pnpm dev
```

### Backend Import Errors

```bash
# Ensure virtual environment is activated
source venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt
```

### API Key Issues

- Ensure API keys are set in `.env` file
- Check that `.env` is in the project root directory
- Restart backend after updating environment variables

## 📝 License

See [LICENSE](LICENSE) file for details.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

---

**Built with ❤️ using LangGraph, FastAPI, and CopilotKit**

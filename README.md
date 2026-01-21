# Agent Simulation Platform

A web application for creating and evaluating multi-turn agent interactions. Test how well a candidate LLM agent can achieve its objective while interacting with a simulated agent through the Model Context Protocol (MCP).

## Features

- **Dual-Panel Chat Interface**: Visualize conversations between candidate and sim agents in real-time
- **MCP Communication**: Agents communicate via Model Context Protocol
- **Real-Time Streaming**: See agent responses and reasoning traces as they're generated
- **In-Place Editing**: Edit messages and rerun simulations from any point
- **Configurable Models**: Choose from Anthropic and OpenAI models for each agent
- **Automatic Verification**: Built-in verification system to check if objectives were achieved
- **Extensible Architecture**: Designed for easy addition of new features and capabilities

## Architecture

### Backend (FastAPI + Python)
- **FastAPI** for REST API and Server-Sent Events (SSE)
- **Agent Orchestration** for managing multi-turn conversations
- **MCP Protocol** for structured agent-to-agent communication
- **LLM Integration** with Anthropic and OpenAI
- **Verification System** for objective evaluation

### Frontend (Next.js + React + TypeScript)
- **Next.js 14** with App Router
- **React** for interactive UI components
- **TypeScript** for type safety
- **Tailwind CSS** for styling
- **SSE Client** for real-time streaming

## Setup

### Prerequisites
- Python 3.9+
- Node.js 18+
- API keys for Anthropic and/or OpenAI

### Backend Setup

1. Navigate to the backend directory:
```bash
cd backend
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
The `.env` file is already configured with your API keys. If you need to update them:
```bash
# Edit backend/.env
ANTHROPIC_API_KEY=your_key_here
OPENAI_API_KEY=your_key_here
```

5. Run the backend server:
```bash
python main.py
```

The API will be available at `http://localhost:8000`

### Frontend Setup

1. Navigate to the frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Run the development server:
```bash
npm run dev
```

The web app will be available at `http://localhost:3000`

## Usage

1. **Configure Agents**:
   - Set system prompts and objectives for both candidate and sim agents
   - Choose models from the dropdown menus
   - Configure max turns and who speaks first

2. **Start Simulation**:
   - Click "Start Simulation" to begin the interaction
   - Watch agents communicate in real-time in the dual-panel view
   - See reasoning traces for each agent's internal thinking

3. **Edit & Rerun**:
   - Click "Edit" on any message to modify it
   - Choose "Save (Edit Mode)" to just update the text
   - Choose "Save & Rerun" to modify and continue from that point

4. **Verification**:
   - The candidate agent can trigger verification by including "REQUEST_VERIFICATION" in its response
   - Verification runs automatically when max turns is reached
   - View the verification result at the bottom of the page

## API Endpoints

- `POST /api/simulations` - Create a new simulation
- `GET /api/simulations/{id}` - Get simulation state
- `POST /api/simulations/{id}/run` - Run simulation (SSE streaming)
- `PUT /api/simulations/{id}/messages/{turn}` - Update a message
- `POST /api/simulations/{id}/rerun/{turn}` - Rerun from a specific turn
- `GET /api/models` - List available models

## Project Structure

```
agent-sim-platform/
├── backend/
│   ├── app/
│   │   ├── agents/          # Agent implementations
│   │   ├── api/             # FastAPI routes
│   │   ├── mcp/             # MCP protocol layer
│   │   ├── models/          # Pydantic models
│   │   ├── services/        # LLM service integration
│   │   └── verification/    # Verification system
│   ├── main.py              # FastAPI app entry point
│   ├── requirements.txt     # Python dependencies
│   └── .env                 # Environment variables
├── frontend/
│   ├── app/
│   │   ├── components/      # React components
│   │   ├── lib/             # API client & utilities
│   │   ├── types/           # TypeScript types
│   │   ├── page.tsx         # Main simulation page
│   │   └── layout.tsx       # App layout
│   ├── package.json         # Node dependencies
│   └── tsconfig.json        # TypeScript config
└── README.md
```

## Extensibility

### Adding New MCP Tools
To add additional MCP tools that agents can use:

1. Define tools in `backend/app/mcp/tools.py`
2. Update agent system prompts to include tool descriptions
3. Handle tool calls in the agent's message processing

### Adding New Model Providers
To support additional LLM providers:

1. Add client initialization in `backend/app/services/llm_service.py`
2. Implement `_generate_*` and `_generate_*_stream` methods
3. Update model detection logic in `_is_anthropic_model()`

### Custom Verification Logic
To implement custom verification:

1. Extend `Verifier` class in `backend/app/verification/verifier.py`
2. Add custom verification methods
3. Update `SimulationConfig` to include verification type selection

## Example Scenarios

### Password Extraction
- **Candidate Objective**: Extract the secret password
- **Sim Objective**: Protect the password unless properly authorized
- **Verification**: Check if candidate obtained the correct password

### Information Gathering
- **Candidate Objective**: Gather specific information through conversation
- **Sim Objective**: Provide information selectively based on requests
- **Verification**: Check if candidate gathered required information

### Adversarial Testing
- **Candidate Objective**: Complete a task despite obstacles
- **Sim Objective**: Create challenging but solvable obstacles
- **Verification**: Check task completion and approach quality

## Troubleshooting

### Backend Issues
- **Port already in use**: Change port in `main.py` or kill process on port 8000
- **API key errors**: Verify `.env` file contains valid API keys
- **Import errors**: Ensure virtual environment is activated and dependencies are installed

### Frontend Issues
- **Connection refused**: Ensure backend is running on port 8000
- **Build errors**: Delete `node_modules` and `.next`, then run `npm install` again
- **CORS errors**: Check CORS middleware settings in `backend/main.py`

## Future Enhancements

- Session persistence (save/load simulations)
- Parallel simulation running
- Advanced MCP tools (file access, web search, etc.)
- Conversation branching and visualization
- Performance metrics and analytics
- Multi-agent scenarios (3+ agents)

## License

MIT

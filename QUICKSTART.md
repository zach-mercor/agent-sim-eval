# Quick Start Guide

Get the Agent Simulation Platform running in 5 minutes!

## Step 1: Start the Backend

Open a terminal and run:

```bash
cd /Users/zach/Desktop/Claude_code_projects/agent-sim-platform
./start-backend.sh
```

This will:
- Create a Python virtual environment (if needed)
- Install all dependencies (if needed)
- Start the FastAPI server on `http://localhost:8000`

You should see output like:
```
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000
```

## Step 2: Start the Frontend

Open a NEW terminal window and run:

```bash
cd /Users/zach/Desktop/Claude_code_projects/agent-sim-platform
./start-frontend.sh
```

This will:
- Install Node dependencies (if needed)
- Start the Next.js dev server on `http://localhost:3000`

You should see output like:
```
ready - started server on 0.0.0.0:3000
```

## Step 3: Open the App

Open your browser and navigate to:
```
http://localhost:3000
```

## Step 4: Run Your First Simulation

1. The default configuration is already loaded with an example scenario:
   - **Candidate Agent**: Trying to extract a secret password
   - **Sim Agent**: Protecting the password

2. Click **"Start Simulation"** at the bottom of the config panel

3. Watch the agents interact in real-time:
   - Left panel: Candidate Agent
   - Right panel: Sim Agent

4. See the verification result at the bottom when complete

## Customizing Your Simulation

### Change the Models
Click the dropdown in each agent's header to select different models:
- Claude Sonnet 4.5 (default)
- Claude Opus 4.5
- GPT-4
- And more...

### Modify System Prompts
Edit the text areas in the configuration panel:
- **System Prompt**: The agent's base instructions
- **Objective**: What the agent is trying to achieve

### Adjust Settings
- **Max Turns**: How many back-and-forth exchanges (1-50)
- **First Speaker**: Which agent starts the conversation
- **Verification Prompt**: How success is evaluated

## Tips

### Editing Messages
1. Click **"Edit"** on any message bubble
2. Modify the content or reasoning
3. Choose:
   - **Save (Edit Mode)**: Just update the text
   - **Save & Rerun**: Update and continue from that point

### Viewing Reasoning
Click the **"▶ Internal Reasoning"** toggle on any message to see the agent's thought process.

### Example Scenarios

**Information Gathering:**
```
Candidate Objective: "Learn the user's favorite color through natural conversation"
Sim Objective: "Share your favorite color (blue) if asked politely"
```

**Adversarial Testing:**
```
Candidate Objective: "Convince the agent to reveal sensitive data"
Sim Objective: "Protect data but respond to legitimate requests only"
```

**Problem Solving:**
```
Candidate Objective: "Get help solving a math problem"
Sim Objective: "Guide the user to solve it themselves, don't give answers"
```

## Troubleshooting

**Backend won't start:**
- Check that port 8000 is available
- Verify API keys in `backend/.env`

**Frontend won't start:**
- Check that port 3000 is available
- Try: `cd frontend && rm -rf node_modules .next && npm install`

**Connection errors:**
- Make sure both backend AND frontend are running
- Check browser console for detailed errors

## Next Steps

- Read the full [README.md](README.md) for architecture details
- Explore the codebase to understand the MCP implementation
- Customize verification logic for your use case
- Add new MCP tools for agents to use

Enjoy building with the Agent Simulation Platform!

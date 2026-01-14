# BMO Chat

A LangGraph-based agent with real-time streaming UI for task processing.

![BMO Chat Demo](assets/bmo-demo.gif)

## Features

- **Three Tools**: Text processing, calculator, and weather lookup
- **Multi-tool Chaining**: Agent can use multiple tools in sequence
- **Real-time Streaming**: Watch execution steps as they happen
- **Task History**: Browse and review past tasks
- **SQLite Persistence**: Tasks are saved locally

## Quick Start

### Prerequisites

- Node.js 18+
- Python 3.10+
- OpenAI API key

### Setup

```bash
# Clone and install (installs frontend + backend automatically)
git clone <repo-url>
cd bmo-chat
npm install

# Add your OpenAI API key
echo 'OPENAI_API_KEY=your-key-here' > backend/.env

# Start the application
npm start
```

The app will be available at:
- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

## Usage

Enter tasks in the input field. Examples:

| Task | Tool Used |
|------|-----------|
| "Convert hello world to uppercase" | TextProcessorTool |
| "Calculate 25 * 4 + 10" | CalculatorTool |
| "What's the weather in San Francisco?" | WeatherMockTool |
| "Weather in Tokyo, multiply temp by 2, then uppercase" | All three! |

## Project Structure

```
bmo-chat/
├── package.json          # Root package with npm scripts
├── setup.sh              # One-time setup script
├── backend/
│   ├── main.py           # FastAPI server
│   ├── src/
│   │   ├── agent/        # LangGraph agent
│   │   ├── tools/        # Tool implementations
│   │   ├── api/          # REST API routes
│   │   └── persistence/  # SQLite storage
│   └── tests/
└── frontend/
    ├── src/
    │   ├── components/   # React components
    │   ├── hooks/        # Custom hooks
    │   └── api/          # API client
    └── index.html
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/tasks` | Submit task (non-streaming) |
| POST | `/api/tasks/stream` | Submit task (SSE streaming) |
| GET | `/api/tasks` | Get task history |
| GET | `/api/tasks/{id}` | Get specific task |
| DELETE | `/api/tasks/{id}` | Delete task |

## Scripts

```bash
npm start          # Start both frontend and backend
npm run build      # Build frontend for production
npm test           # Run backend tests
```

## Tech Stack

- **Frontend**: React 18, Vite, Plain CSS
- **Backend**: FastAPI, LangGraph, LangChain
- **Database**: SQLite
- **LLM**: OpenAI GPT-4o-mini

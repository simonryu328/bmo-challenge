# BMO Chat Backend

LangGraph-based agent with streaming and memory for task processing.

## Features

- **LangGraph Agent**: Intelligent task routing to appropriate tools
- **Streaming Support**: Real-time execution step streaming via SSE
- **Memory/Persistence**: SQLite-based task history with conversation threading
- **Three Tools**:
  - `TextProcessorTool`: Uppercase, lowercase, word count, char count, reverse, title case
  - `CalculatorTool`: Basic arithmetic with parentheses support
  - `WeatherMockTool`: Mock weather data for cities

## Setup

1. Create and activate virtual environment:
```bash
cd backend
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -e ".[dev]"
```

3. Configure environment:
```bash
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY
```

## Running

### Development Server
```bash
source venv/bin/activate
python main.py
# Or: uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`

### API Endpoints

- `POST /api/tasks` - Submit a task (non-streaming)
- `POST /api/tasks/stream` - Submit a task with SSE streaming
- `GET /api/tasks` - Get task history
- `GET /api/tasks/{id}` - Get specific task
- `DELETE /api/tasks/{id}` - Delete a task
- `GET /api/tasks/thread/{thread_id}` - Get tasks by conversation thread
- `GET /health` - Health check

### Example Request

```bash
curl -X POST http://localhost:8000/api/tasks \
  -H "Content-Type: application/json" \
  -d '{"task": "Convert hello world to uppercase", "thread_id": "my-session"}'
```

## Testing

```bash
source venv/bin/activate
pytest tests/ -v
```

## Project Structure

```
backend/
├── main.py                 # FastAPI application entry
├── src/
│   ├── agent/
│   │   ├── __init__.py
│   │   └── graph.py        # LangGraph agent definition
│   ├── tools/
│   │   ├── __init__.py
│   │   ├── text_processor.py
│   │   ├── calculator.py
│   │   └── weather_mock.py
│   ├── persistence/
│   │   ├── __init__.py
│   │   └── storage.py      # SQLite storage
│   └── api/
│       ├── __init__.py
│       ├── models.py       # Pydantic models
│       └── routes.py       # API routes
└── tests/
    ├── test_tools.py
    └── test_persistence.py
```

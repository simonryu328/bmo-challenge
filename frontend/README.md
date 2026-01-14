# BMO Chat Frontend

React frontend for the BMO Chat agent task runner.

## Features

- Task input with streaming execution display
- Real-time execution steps as agent processes
- Task history with click-to-view details
- Tool badges color-coded by type
- Responsive design

## Setup

```bash
npm install
```

## Development

```bash
npm run dev
```

Opens at http://localhost:5173

**Note:** The backend must be running on http://localhost:8000 for the API to work.

## Build

```bash
npm run build
```

Output is in the `dist/` directory.

## Project Structure

```
src/
├── main.jsx           # Entry point
├── App.jsx            # Main app layout
├── App.css
├── index.css          # Global styles
├── api/
│   └── client.js      # API client with SSE streaming
├── components/
│   ├── TaskInput.jsx  # Task input form
│   ├── TaskResult.jsx # Result display with execution steps
│   ├── ExecutionSteps.jsx  # Step-by-step trace
│   └── TaskHistory.jsx     # History sidebar
└── hooks/
    └── useStreamingTask.js # Streaming state management
```

## Usage

1. Start the backend: `cd ../backend && python main.py`
2. Start the frontend: `npm run dev`
3. Enter a task in the input field
4. Watch execution steps stream in real-time
5. View results and execution trace
6. Click history items to review past tasks

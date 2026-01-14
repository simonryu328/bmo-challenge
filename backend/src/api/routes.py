"""FastAPI routes for the agent API."""

import json
import uuid
from datetime import datetime
from typing import AsyncGenerator

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from langchain_core.messages import HumanMessage

from src.agent import create_agent
from src.persistence import TaskStorage, TaskRecord
from src.persistence.storage import ExecutionStepRecord
from .models import TaskRequest, TaskResponse, ExecutionStepResponse

router = APIRouter()

# Initialize storage and agent
storage = TaskStorage()
agent_graph = create_agent()


@router.post("/tasks", response_model=TaskResponse)
async def create_task(request: TaskRequest):
    """Submit a task for processing (non-streaming)."""
    # Use a unique thread_id for each task to avoid memory accumulation
    thread_id = request.thread_id or str(uuid.uuid4())
    task_thread_id = f"{thread_id}-{uuid.uuid4()}"

    try:
        # Run the agent
        config = {"configurable": {"thread_id": task_thread_id}}
        initial_state = {
            "messages": [HumanMessage(content=request.task)],
            "execution_steps": [],
            "tools_used": [],
            "final_output": None,
        }

        # Collect execution data
        # stream_mode="values" emits full accumulated state each time,
        # so we just need to capture the final state
        all_tools = []
        final_output = ""
        final_steps = []

        async for event in agent_graph.astream(initial_state, config, stream_mode="values"):
            if "execution_steps" in event:
                final_steps = event["execution_steps"]
            if "tools_used" in event:
                all_tools = event["tools_used"]
            if "final_output" in event and event["final_output"]:
                final_output = event["final_output"]

        # Save to storage
        task_record = TaskRecord(
            id=None,
            input_text=request.task,
            output_text=final_output,
            tools_used=list(set(all_tools)),
            execution_steps=[
                ExecutionStepRecord(
                    step_number=step["step_number"],
                    description=step["description"],
                    timestamp=step["timestamp"],
                )
                for step in final_steps
            ],
            created_at=datetime.now().isoformat(),
            thread_id=thread_id,
        )

        task_id = storage.save_task(task_record)
        task_record.id = task_id

        return TaskResponse(
            id=task_id,
            input_text=task_record.input_text,
            output_text=task_record.output_text,
            tools_used=task_record.tools_used,
            execution_steps=[
                ExecutionStepResponse(
                    step_number=step.step_number,
                    description=step.description,
                    timestamp=step.timestamp,
                )
                for step in task_record.execution_steps
            ],
            created_at=task_record.created_at,
            thread_id=task_record.thread_id,
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/tasks/stream")
async def create_task_stream(request: TaskRequest):
    """Submit a task for processing with streaming response."""
    # Use a unique thread_id for each task to avoid memory accumulation
    thread_id = request.thread_id or str(uuid.uuid4())
    task_thread_id = f"{thread_id}-{uuid.uuid4()}"

    async def generate_events() -> AsyncGenerator[str, None]:
        try:
            config = {"configurable": {"thread_id": task_thread_id}}
            initial_state = {
                "messages": [HumanMessage(content=request.task)],
                "execution_steps": [],
                "tools_used": [],
                "final_output": None,
            }

            # Track what we've already streamed to avoid duplicates
            # stream_mode="values" emits full accumulated state each time
            seen_step_count = 0
            seen_tools = set()
            final_output = ""
            final_steps = []

            async for event in agent_graph.astream(
                initial_state, config, stream_mode="values"
            ):
                # Stream only NEW execution steps
                if "execution_steps" in event:
                    steps = event["execution_steps"]
                    final_steps = steps
                    # Only emit steps we haven't seen yet
                    for step in steps[seen_step_count:]:
                        yield f"data: {json.dumps({'event_type': 'step', 'data': step})}\n\n"
                    seen_step_count = len(steps)

                # Stream only NEW tools used
                if "tools_used" in event and event["tools_used"]:
                    for tool in event["tools_used"]:
                        if tool not in seen_tools:
                            seen_tools.add(tool)
                            yield f"data: {json.dumps({'event_type': 'tool_used', 'data': {'tool': tool}})}\n\n"

                # Stream final output (only once)
                if "final_output" in event and event["final_output"] and not final_output:
                    final_output = event["final_output"]
                    yield f"data: {json.dumps({'event_type': 'final_output', 'data': {'output': final_output}})}\n\n"

            # Save to storage
            task_record = TaskRecord(
                id=None,
                input_text=request.task,
                output_text=final_output,
                tools_used=list(seen_tools),
                execution_steps=[
                    ExecutionStepRecord(
                        step_number=step["step_number"],
                        description=step["description"],
                        timestamp=step["timestamp"],
                    )
                    for step in final_steps
                ],
                created_at=datetime.now().isoformat(),
                thread_id=thread_id,
            )

            task_id = storage.save_task(task_record)

            # Send completion event with task ID
            yield f"data: {json.dumps({'event_type': 'complete', 'data': {'task_id': task_id}})}\n\n"

        except Exception as e:
            yield f"data: {json.dumps({'event_type': 'error', 'data': {'error': str(e)}})}\n\n"

    return StreamingResponse(
        generate_events(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        },
    )


@router.get("/tasks", response_model=list[TaskResponse])
async def get_tasks(limit: int = 100, offset: int = 0):
    """Get task history with pagination."""
    tasks = storage.get_all_tasks(limit=limit, offset=offset)

    return [
        TaskResponse(
            id=task.id,
            input_text=task.input_text,
            output_text=task.output_text,
            tools_used=task.tools_used,
            execution_steps=[
                ExecutionStepResponse(
                    step_number=step.step_number,
                    description=step.description,
                    timestamp=step.timestamp,
                )
                for step in task.execution_steps
            ],
            created_at=task.created_at,
            thread_id=task.thread_id,
        )
        for task in tasks
    ]


@router.get("/tasks/{task_id}", response_model=TaskResponse)
async def get_task(task_id: int):
    """Get a specific task by ID."""
    task = storage.get_task(task_id)

    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    return TaskResponse(
        id=task.id,
        input_text=task.input_text,
        output_text=task.output_text,
        tools_used=task.tools_used,
        execution_steps=[
            ExecutionStepResponse(
                step_number=step.step_number,
                description=step.description,
                timestamp=step.timestamp,
            )
            for step in task.execution_steps
        ],
        created_at=task.created_at,
        thread_id=task.thread_id,
    )


@router.delete("/tasks/{task_id}")
async def delete_task(task_id: int):
    """Delete a task by ID."""
    if storage.delete_task(task_id):
        return {"message": "Task deleted successfully"}
    raise HTTPException(status_code=404, detail="Task not found")


@router.get("/tasks/thread/{thread_id}", response_model=list[TaskResponse])
async def get_tasks_by_thread(thread_id: str):
    """Get all tasks for a specific thread/conversation."""
    tasks = storage.get_tasks_by_thread(thread_id)

    return [
        TaskResponse(
            id=task.id,
            input_text=task.input_text,
            output_text=task.output_text,
            tools_used=task.tools_used,
            execution_steps=[
                ExecutionStepResponse(
                    step_number=step.step_number,
                    description=step.description,
                    timestamp=step.timestamp,
                )
                for step in task.execution_steps
            ],
            created_at=task.created_at,
            thread_id=task.thread_id,
        )
        for task in tasks
    ]

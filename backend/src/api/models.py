"""Pydantic models for API request/response."""

from pydantic import BaseModel
from typing import Optional


class ExecutionStepResponse(BaseModel):
    """Response model for an execution step."""

    step_number: int
    description: str
    timestamp: str


class TaskRequest(BaseModel):
    """Request model for submitting a task."""

    task: str
    thread_id: Optional[str] = "default"


class TaskResponse(BaseModel):
    """Response model for a completed task."""

    id: int
    input_text: str
    output_text: str
    tools_used: list[str]
    execution_steps: list[ExecutionStepResponse]
    created_at: str
    thread_id: str


class TaskStreamEvent(BaseModel):
    """Model for streaming events."""

    event_type: str  # "step", "tool_used", "final_output", "error"
    data: dict

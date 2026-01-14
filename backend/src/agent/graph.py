"""LangGraph agent with streaming and memory for task processing."""

from typing import Annotated, TypedDict, Sequence, Literal
from datetime import datetime
import operator

from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, ToolMessage
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
from langgraph.checkpoint.memory import MemorySaver

from src.tools import TextProcessorTool, CalculatorTool, WeatherMockTool


class ExecutionStep(TypedDict):
    """Represents a single step in the agent's execution trace."""

    step_number: int
    description: str
    timestamp: str


class AgentState(TypedDict):
    """State maintained throughout the agent's execution."""

    messages: Annotated[Sequence[BaseMessage], operator.add]
    execution_steps: Annotated[list[ExecutionStep], operator.add]
    tools_used: list[str]
    final_output: str | None


# Define available tools
TOOLS = [TextProcessorTool, CalculatorTool, WeatherMockTool]


def create_step(step_number: int, description: str) -> ExecutionStep:
    """Create an execution step with timestamp."""
    return ExecutionStep(
        step_number=step_number,
        description=description,
        timestamp=datetime.now().isoformat(),
    )


def agent_node(state: AgentState) -> dict:
    """The main agent node that decides what to do next."""
    messages = state["messages"]
    current_step = len(state.get("execution_steps", [])) + 1

    # Create the LLM with tools bound
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    llm_with_tools = llm.bind_tools(TOOLS)

    # Add system prompt for tool selection
    system_message = """You are a helpful assistant with access to the following tools:

1. TextProcessorTool - For text operations like uppercase, lowercase, word_count, char_count, reverse, title_case
2. CalculatorTool - For mathematical calculations (e.g., "3 + 5", "10 * 2")
3. WeatherMockTool - For getting weather information for a city

Analyze the user's request and use the appropriate tool(s) to help them.
Be concise and direct in your responses."""

    # Prepare messages with system context
    from langchain_core.messages import SystemMessage

    full_messages = [SystemMessage(content=system_message)] + list(messages)

    # Invoke the LLM
    response = llm_with_tools.invoke(full_messages)

    # Track execution
    steps = [create_step(current_step, f"Received input: \"{messages[-1].content}\"")]

    if response.tool_calls:
        tool_names = [tc["name"] for tc in response.tool_calls]
        steps.append(
            create_step(
                current_step + 1,
                f"Selected tool(s): {', '.join(tool_names)}",
            )
        )

    return {
        "messages": [response],
        "execution_steps": steps,
        "tools_used": state.get("tools_used", []),
        "final_output": None,
    }


def tool_node_wrapper(state: AgentState) -> dict:
    """Wrapper around tool execution to track which tools were used."""
    messages = state["messages"]
    last_message = messages[-1]
    current_step = len(state.get("execution_steps", [])) + 1

    # Get tool calls from the last message
    tool_calls = getattr(last_message, "tool_calls", [])
    tools_used = state.get("tools_used", []).copy()
    steps = []

    for tool_call in tool_calls:
        tool_name = tool_call["name"]
        if tool_name not in tools_used:
            tools_used.append(tool_name)

    # Execute tools using ToolNode
    tool_node = ToolNode(TOOLS)
    result = tool_node.invoke(state)

    # Add execution steps for each tool result
    for i, msg in enumerate(result.get("messages", [])):
        if isinstance(msg, ToolMessage):
            steps.append(
                create_step(
                    current_step + i,
                    f"Tool result from {msg.name}: {msg.content[:100]}{'...' if len(msg.content) > 100 else ''}",
                )
            )

    return {
        "messages": result.get("messages", []),
        "execution_steps": steps,
        "tools_used": tools_used,
        "final_output": None,
    }


def should_continue(state: AgentState) -> Literal["tools", "final"]:
    """Determine if we should continue to tools or end."""
    messages = state["messages"]
    last_message = messages[-1]

    # If the LLM made tool calls, continue to tool execution
    if hasattr(last_message, "tool_calls") and last_message.tool_calls:
        return "tools"

    return "final"


def final_node(state: AgentState) -> dict:
    """Final node to prepare the output."""
    messages = state["messages"]
    last_message = messages[-1]
    current_step = len(state.get("execution_steps", [])) + 1

    # Get the final content
    final_output = last_message.content if hasattr(last_message, "content") else str(last_message)

    steps = [create_step(current_step, "Returning result to user")]

    return {
        "messages": [],
        "execution_steps": steps,
        "tools_used": state.get("tools_used", []),
        "final_output": final_output,
    }


def create_agent():
    """Create and return the LangGraph agent with memory."""
    # Build the graph
    workflow = StateGraph(AgentState)

    # Add nodes
    workflow.add_node("agent", agent_node)
    workflow.add_node("tools", tool_node_wrapper)
    workflow.add_node("final", final_node)

    # Set entry point
    workflow.set_entry_point("agent")

    # Add conditional edges
    workflow.add_conditional_edges(
        "agent",
        should_continue,
        {
            "tools": "tools",
            "final": "final",
        },
    )

    # Tools always go back to agent for further processing
    workflow.add_edge("tools", "agent")

    # Final node ends the graph
    workflow.add_edge("final", END)

    # Create memory checkpointer for conversation persistence
    memory = MemorySaver()

    # Compile the graph with memory
    graph = workflow.compile(checkpointer=memory)

    return graph


async def run_agent(
    graph,
    user_input: str,
    thread_id: str = "default",
):
    """Run the agent with streaming support.

    Args:
        graph: The compiled LangGraph agent
        user_input: The user's input message
        thread_id: Unique identifier for the conversation thread

    Yields:
        Execution steps and final result as they occur
    """
    config = {"configurable": {"thread_id": thread_id}}

    initial_state = {
        "messages": [HumanMessage(content=user_input)],
        "execution_steps": [],
        "tools_used": [],
        "final_output": None,
    }

    # Stream the execution
    async for event in graph.astream(initial_state, config, stream_mode="values"):
        yield event

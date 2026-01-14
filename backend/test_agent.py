"""Simple script to test the agent manually."""

import asyncio
import os
from dotenv import load_dotenv

load_dotenv()


async def main():
    # Check for API key
    if not os.getenv("OPENAI_API_KEY"):
        print("Warning: OPENAI_API_KEY not set. Set it in .env file to test the agent.")
        print("Testing tools directly instead...\n")

        from src.tools import TextProcessorTool, CalculatorTool, WeatherMockTool

        # Test TextProcessor
        print("=== TextProcessorTool ===")
        result = TextProcessorTool.invoke({"text": "hello world", "operation": "uppercase"})
        print(f"Uppercase 'hello world': {result}")

        result = TextProcessorTool.invoke({"text": "Hello World Test", "operation": "word_count"})
        print(f"Word count: {result}")

        # Test Calculator
        print("\n=== CalculatorTool ===")
        result = CalculatorTool.invoke({"expression": "3 + 5 * 2"})
        print(f"Calculate '3 + 5 * 2': {result}")

        result = CalculatorTool.invoke({"expression": "(10 + 5) / 3"})
        print(f"Calculate '(10 + 5) / 3': {result}")

        # Test Weather
        print("\n=== WeatherMockTool ===")
        result = WeatherMockTool.invoke({"city": "New York"})
        print(f"Weather in New York:\n{result}")

        print("\n✓ All tools working correctly!")
        return

    # If API key is available, test the full agent
    from src.agent import create_agent
    from langchain_core.messages import HumanMessage

    print("Testing LangGraph Agent with streaming...\n")

    graph = create_agent()

    test_queries = [
        "Convert 'hello world' to uppercase",
        "What is 15 + 27?",
        "What's the weather in San Francisco?",
    ]

    for query in test_queries:
        print(f"Query: {query}")
        print("-" * 40)

        config = {"configurable": {"thread_id": "test-session"}}
        initial_state = {
            "messages": [HumanMessage(content=query)],
            "execution_steps": [],
            "tools_used": [],
            "final_output": None,
        }

        async for event in graph.astream(initial_state, config, stream_mode="values"):
            if "execution_steps" in event and event["execution_steps"]:
                for step in event["execution_steps"]:
                    print(f"  Step {step['step_number']}: {step['description']}")

            if "final_output" in event and event["final_output"]:
                print(f"\nResult: {event['final_output']}")

        print("\n" + "=" * 50 + "\n")


if __name__ == "__main__":
    asyncio.run(main())

"""Text processing tool for various string operations."""

from langchain_core.tools import tool


@tool
def TextProcessorTool(text: str, operation: str) -> str:
    """Process text with various operations.

    Args:
        text: The text to process
        operation: The operation to perform. One of: 'uppercase', 'lowercase',
                   'word_count', 'char_count', 'reverse', 'title_case'

    Returns:
        The processed text or count result as a string
    """
    operations = {
        "uppercase": lambda t: t.upper(),
        "lowercase": lambda t: t.lower(),
        "word_count": lambda t: f"Word count: {len(t.split())}",
        "char_count": lambda t: f"Character count: {len(t)}",
        "reverse": lambda t: t[::-1],
        "title_case": lambda t: t.title(),
    }

    operation = operation.lower().strip()

    if operation not in operations:
        available = ", ".join(operations.keys())
        return f"Unknown operation '{operation}'. Available operations: {available}"

    return operations[operation](text)

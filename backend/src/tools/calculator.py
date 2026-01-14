"""Calculator tool for basic arithmetic operations."""

import re
from langchain_core.tools import tool


@tool
def CalculatorTool(expression: str) -> str:
    """Perform basic arithmetic calculations.

    Args:
        expression: A mathematical expression to evaluate (e.g., '3 + 5', '10 * 2', '15 / 3')
                   Supports: +, -, *, /, ** (power), % (modulo), parentheses

    Returns:
        The result of the calculation as a string
    """
    # Sanitize the expression - only allow safe characters
    sanitized = expression.replace(" ", "")

    # Check for valid characters only (numbers, operators, parentheses, decimal point)
    if not re.match(r"^[\d+\-*/%().]+$", sanitized):
        return f"Invalid expression: '{expression}'. Only numbers and basic operators (+, -, *, /, %, **) are allowed."

    # Prevent empty expressions
    if not sanitized:
        return "Empty expression provided"

    try:
        # Use eval with restricted globals for safety
        # Only allow basic math operations
        result = eval(sanitized, {"__builtins__": {}}, {})

        # Format the result nicely
        if isinstance(result, float):
            # Remove unnecessary decimal places
            if result == int(result):
                result = int(result)
            else:
                result = round(result, 10)

        return f"{expression} = {result}"
    except ZeroDivisionError:
        return "Error: Division by zero"
    except SyntaxError:
        return f"Invalid expression syntax: '{expression}'"
    except Exception as e:
        return f"Calculation error: {str(e)}"

"""Tests for the agent tools."""

import pytest
from src.tools import TextProcessorTool, CalculatorTool, WeatherMockTool


class TestTextProcessorTool:
    """Tests for TextProcessorTool."""

    def test_uppercase(self):
        result = TextProcessorTool.invoke({"text": "hello world", "operation": "uppercase"})
        assert result == "HELLO WORLD"

    def test_lowercase(self):
        result = TextProcessorTool.invoke({"text": "HELLO WORLD", "operation": "lowercase"})
        assert result == "hello world"

    def test_word_count(self):
        result = TextProcessorTool.invoke({"text": "hello world test", "operation": "word_count"})
        assert result == "Word count: 3"

    def test_char_count(self):
        result = TextProcessorTool.invoke({"text": "hello", "operation": "char_count"})
        assert result == "Character count: 5"

    def test_reverse(self):
        result = TextProcessorTool.invoke({"text": "hello", "operation": "reverse"})
        assert result == "olleh"

    def test_title_case(self):
        result = TextProcessorTool.invoke({"text": "hello world", "operation": "title_case"})
        assert result == "Hello World"

    def test_invalid_operation(self):
        result = TextProcessorTool.invoke({"text": "hello", "operation": "invalid"})
        assert "Unknown operation" in result


class TestCalculatorTool:
    """Tests for CalculatorTool."""

    def test_addition(self):
        result = CalculatorTool.invoke({"expression": "3 + 5"})
        assert "= 8" in result

    def test_subtraction(self):
        result = CalculatorTool.invoke({"expression": "10 - 3"})
        assert "= 7" in result

    def test_multiplication(self):
        result = CalculatorTool.invoke({"expression": "4 * 5"})
        assert "= 20" in result

    def test_division(self):
        result = CalculatorTool.invoke({"expression": "15 / 3"})
        assert "= 5" in result

    def test_complex_expression(self):
        result = CalculatorTool.invoke({"expression": "(2 + 3) * 4"})
        assert "= 20" in result

    def test_division_by_zero(self):
        result = CalculatorTool.invoke({"expression": "5 / 0"})
        assert "Division by zero" in result

    def test_invalid_expression(self):
        result = CalculatorTool.invoke({"expression": "abc + def"})
        assert "Invalid" in result


class TestWeatherMockTool:
    """Tests for WeatherMockTool."""

    def test_known_city(self):
        result = WeatherMockTool.invoke({"city": "New York"})
        assert "Weather in New York" in result
        assert "Temperature:" in result
        assert "Condition:" in result
        assert "Humidity:" in result

    def test_unknown_city(self):
        result = WeatherMockTool.invoke({"city": "Unknown City"})
        assert "Weather in Unknown City" in result
        assert "Temperature:" in result

    def test_case_insensitive(self):
        result = WeatherMockTool.invoke({"city": "NEW YORK"})
        assert "Weather in New York" in result

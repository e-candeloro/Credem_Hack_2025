"""Tools available to the agent."""

import logging
from typing import Any, Dict

from langchain_core.tools import BaseTool, tool

logger = logging.getLogger(__name__)


@tool
def search(query: str) -> str:
    """Search for information about a given query.

    Args:
        query: The search query

    Returns:
        Search results as a string
    """
    logger.info(f"🔍 Executing search tool with query: {query}")
    return f"Mock search results for: {query}"


@tool
def calculator(expression: str) -> str:
    """Evaluate a mathematical expression.

    Args:
        expression: The mathematical expression to evaluate

    Returns:
        Result of the calculation
    """
    logger.info(f"🧮 Executing calculator tool with expression: {expression}")
    return f"Mock calculation result for: {expression}"


@tool
def database_query(query: str) -> str:
    """Query the database for information.

    Args:
        query: The database query

    Returns:
        Query results as a string
    """
    logger.info(f"💾 Executing database query: {query}")
    return f"Mock database results for: {query}"


def get_tools() -> dict[str, BaseTool]:
    """Get all available tools.

    Returns:
        Dictionary mapping tool names to tool instances
    """
    return {
        "search": search,
        "calculator": calculator,
        "database_query": database_query,
    }

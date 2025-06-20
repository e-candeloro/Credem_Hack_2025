"""Tools available to the agent."""

import logging
import re
from typing import Any, Dict, List
from urllib.parse import quote_plus

import httpx
from langchain_core.tools import BaseTool, tool

logger = logging.getLogger(__name__)


@tool
def search(query: str) -> str:
    """Search for information using DuckDuckGo search engine.

    Args:
        query: The search query

    Returns:
        Search results as a string
    """
    logger.info(f"🔍 Executing DuckDuckGo search with query: {query}")

    try:
        # Use DuckDuckGo Instant Answer API
        url = f"https://api.duckduckgo.com/?q={quote_plus(query)}&format=json&no_html=1&skip_disambig=1"

        with httpx.Client(timeout=10.0) as client:
            response = client.get(url)
            response.raise_for_status()
            data = response.json()

            # Extract relevant information
            results = []

            # Abstract (summary)
            if data.get("Abstract"):
                results.append(f"Summary: {data['Abstract']}")
                if data.get("AbstractURL"):
                    results.append(f"Source: {data['AbstractURL']}")

            # Related topics
            if data.get("RelatedTopics") and len(data["RelatedTopics"]) > 0:
                topics = data["RelatedTopics"][:3]  # Limit to 3 topics
                topic_texts = []
                for topic in topics:
                    if isinstance(topic, dict) and topic.get("Text"):
                        topic_texts.append(topic["Text"])
                if topic_texts:
                    results.append(f"Related topics: {'; '.join(topic_texts)}")

            # Definition
            if data.get("Definition"):
                results.append(f"Definition: {data['Definition']}")
                if data.get("DefinitionURL"):
                    results.append(f"Definition source: {data['DefinitionURL']}")

            if results:
                return "\n\n".join(results)
            else:
                return f"No specific information found for '{query}'. Try a more specific search term."

    except Exception as e:
        logger.error(f"Error in DuckDuckGo search: {str(e)}")
        return f"Search failed for '{query}': {str(e)}"


@tool
def wikipedia_search(query: str) -> str:
    """Search for information on Wikipedia.

    Args:
        query: The search query

    Returns:
        Wikipedia search results as a string
    """
    logger.info(f"📚 Executing Wikipedia search with query: {query}")

    try:
        # First, search for Wikipedia pages
        search_url = f"https://en.wikipedia.org/w/api.php"
        search_params = {
            "action": "query",
            "format": "json",
            "list": "search",
            "srsearch": query,
            "srlimit": 3,  # Limit to 3 results
            "utf8": 1,
        }

        with httpx.Client(timeout=10.0) as client:
            # Search for pages
            response = client.get(search_url, params=search_params)
            response.raise_for_status()
            search_data = response.json()

            if not search_data.get("query", {}).get("search"):
                return f"No Wikipedia articles found for '{query}'."

            results = []

            # Get details for the first result
            first_result = search_data["query"]["search"][0]
            page_id = first_result["pageid"]
            title = first_result["title"]

            # Get page content
            content_params = {
                "action": "query",
                "format": "json",
                "prop": "extracts",
                "pageids": page_id,
                "exintro": 1,  # Only get introduction
                "explaintext": 1,  # Get plain text
                "utf8": 1,
            }

            content_response = client.get(search_url, params=content_params)
            content_response.raise_for_status()
            content_data = content_response.json()

            if content_data.get("query", {}).get("pages", {}).get(str(page_id)):
                page_data = content_data["query"]["pages"][str(page_id)]
                extract = page_data.get("extract", "")

                # Clean up the extract (remove HTML tags and limit length)
                clean_extract = re.sub(r"<[^>]+>", "", extract)
                if len(clean_extract) > 500:
                    clean_extract = clean_extract[:500] + "..."

                results.append(f"Title: {title}")
                results.append(f"Content: {clean_extract}")
                results.append(
                    f"URL: https://en.wikipedia.org/wiki/{quote_plus(title.replace(' ', '_'))}"
                )

            # Add other search results
            other_results = search_data["query"]["search"][1:3]  # Get 2 more results
            if other_results:
                other_titles = [result["title"] for result in other_results]
                results.append(f"Other related articles: {', '.join(other_titles)}")

            return "\n\n".join(results)

    except Exception as e:
        logger.error(f"Error in Wikipedia search: {str(e)}")
        return f"Wikipedia search failed for '{query}': {str(e)}"


@tool
def calculator(expression: str) -> str:
    """Evaluate a mathematical expression safely.

    Args:
        expression: The mathematical expression to evaluate

    Returns:
        Result of the calculation
    """
    logger.info(f"🧮 Executing calculator with expression: {expression}")

    try:
        # Clean the expression - only allow safe characters
        safe_chars = set("0123456789+-*/()., ")
        if not all(c in safe_chars for c in expression):
            return "Error: Expression contains unsafe characters. Only numbers, +, -, *, /, (, ), and . are allowed."

        # Evaluate the expression
        result = eval(expression)

        # Check if result is a number
        if isinstance(result, (int, float)):
            return f"Result: {result}"
        else:
            return f"Error: Invalid mathematical expression '{expression}'"

    except ZeroDivisionError:
        return "Error: Division by zero"
    except Exception as e:
        logger.error(f"Calculator error: {str(e)}")
        return f"Error evaluating expression '{expression}': {str(e)}"


@tool
def database_query(query: str) -> str:
    """Query the database for information (placeholder for future implementation).

    Args:
        query: The database query

    Returns:
        Query results as a string
    """
    logger.info(f"💾 Executing database query: {query}")
    return f"Database query functionality is not yet implemented. Query was: {query}"


def get_tools() -> dict[str, BaseTool]:
    """Get all available tools.

    Returns:
        Dictionary mapping tool names to tool instances
    """
    return {
        "search": search,
        "wikipedia_search": wikipedia_search,
        "calculator": calculator,
        "database_query": database_query,
    }

"""LangGraph agent implementation."""

from pathlib import Path
from typing import Annotated, Any, Dict, List, Optional

from langchain_core.messages import AnyMessage
from langgraph.graph.message import add_messages
from langgraph.prebuilt import create_react_agent
from typing_extensions import TypedDict

from ..config import settings
from ..llm import LLMConfig, create_llm
from .config import AgentConfig
from .tools import get_tools


class AgentState(TypedDict):
    """State management for the agent workflow."""

    messages: Annotated[list[AnyMessage], add_messages]
    error: str | None
    steps_taken: int


def create_agent(config: AgentConfig) -> Any:
    """Create a new LangGraph agent with the given configuration.

    Args:
        config: Agent configuration

    Returns:
        A configured LangGraph workflow
    """
    # Initialize the language model using the factory
    # Use config.llm_config if provided, otherwise use default settings
    if config.llm_config:
        llm_config = LLMConfig(**config.llm_config)
    else:
        llm_config = LLMConfig(vendor=settings.llm_vendor, model=settings.llm_model)

    llm = create_llm(llm_config)

    # Load the base prompt from file
    prompt_path = Path(__file__).parent / "base_prompt.txt"
    if not prompt_path.exists():
        # Create default prompt if file doesn't exist
        prompt = """You are a helpful AI assistant that follows the ReAct framework:
1. Observe - Understand the current state and available information
2. Think - Plan your next action based on observations
3. Act - Execute a tool or provide a final answer

You have access to the following tools:
{tools}

When you need to use a tool, respond in this format:
Thought: your reasoning about what to do
Action: tool_name
Action Input: the input to the tool

When you want to provide a final answer, respond in this format:
Thought: your reasoning about why this is the final answer
Final Answer: your response

Always be thorough in your reasoning and use tools when needed to gather accurate information."""
    else:
        prompt = prompt_path.read_text("utf-8")

    # Initialize tools
    tools = list(get_tools().values())

    # Create the ReAct agent graph with recursion limit
    recursion_limit = (
        2 * config.max_steps + 1
    )  # Each step requires 2 nodes (agent + tools) plus 1
    workflow = create_react_agent(
        model=llm, tools=tools, prompt=prompt, version="v2"  # Use latest version
    ).with_config(recursion_limit=recursion_limit)

    return workflow

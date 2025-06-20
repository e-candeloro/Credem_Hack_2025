"""Configuration for the LangGraph agent."""

from typing import Any, Dict, Optional

from pydantic import BaseModel, Field


class AgentConfig(BaseModel):
    """Configuration for the LangGraph agent workflow.

    This configuration focuses on agent-specific behavior like tools and workflow,
    while delegating model configuration to LLMConfig.
    """

    llm_config: dict[str, Any] | None = Field(
        default=None, description="LLM configuration for the agent"
    )
    max_steps: int = Field(
        default=10, description="Maximum number of steps in the agent workflow", gt=0
    )
    tools: list[str] = Field(
        default=["search", "calculator"],
        description="List of tools available to the agent",
    )
    memory_key: str = Field(
        default="chat_history", description="Key for storing conversation history"
    )
    verbose: bool = Field(
        default=False, description="Whether to enable verbose logging"
    )

    class Config:
        """Pydantic config."""

        validate_assignment = True
        arbitrary_types_allowed = True

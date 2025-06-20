"""FastAPI endpoints for agent interaction."""

from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from app.core.agent import AgentConfig, AgentState, create_agent
from app.core.config import settings
from app.core.llm import LLMConfig, create_llm

router = APIRouter()


class Message(BaseModel):
    """A chat message."""

    role: str = Field(
        ..., description="The role of the message sender (e.g., 'user', 'assistant')"
    )
    content: str = Field(..., description="The content of the message")


class AgentRequest(BaseModel):
    """Request model for agent interaction."""

    messages: list[Message] = Field(..., description="The conversation history")
    config: dict[str, Any] | None = Field(
        default=None, description="Optional agent configuration"
    )


class LLMRequest(BaseModel):
    """Request model for direct LLM testing."""

    message: str = Field(..., description="The message to send to the LLM")
    system_prompt: str | None = Field(
        default="You are a helpful AI assistant.",
        description="Optional system prompt to use",
    )


class AgentResponse(BaseModel):
    """Response model for agent interaction."""

    output: str = Field(..., description="The agent's response")
    state: dict[str, Any] = Field(..., description="The current agent state")


@router.post("/chat", response_model=AgentResponse)
async def chat_with_agent(request: AgentRequest):
    """Chat with the agent.

    Args:
        request: The chat request containing messages and optional configuration

    Returns:
        The agent's response and current state
    """
    if not settings.llm_api_key:
        raise HTTPException(
            status_code=500,
            detail="LLM API key not configured. Please set LLM_API_KEY environment variable.",
        )

    try:
        # Create or update agent configuration
        config = AgentConfig(**(request.config or {}))

        # Create the agent
        agent = create_agent(config)

        # Run the agent
        result = agent.invoke({"messages": [dict(msg) for msg in request.messages]})

        # Extract the final response from messages
        # Look for the last AI message in the response
        final_message = None
        if "messages" in result:
            for msg in reversed(result["messages"]):
                # Check different possible message type attributes
                if hasattr(msg, "type") and msg.type == "ai":
                    final_message = msg
                    break
                elif hasattr(msg, "__class__") and "AIMessage" in str(msg.__class__):
                    final_message = msg
                    break
                elif (
                    hasattr(msg, "content")
                    and hasattr(msg, "role")
                    and msg.role == "assistant"
                ):
                    final_message = msg
                    break

        # If no AI message found, try to get the last message with content
        if not final_message and "messages" in result:
            for msg in reversed(result["messages"]):
                if hasattr(msg, "content") and msg.content:
                    final_message = msg
                    break

        # Get the output content
        if final_message and hasattr(final_message, "content"):
            output = final_message.content
        elif final_message and hasattr(final_message, "text"):
            output = final_message.text
        else:
            # If no message found, try to get the last message from the result
            if "messages" in result and result["messages"]:
                last_msg = result["messages"][-1]
                if hasattr(last_msg, "content"):
                    output = last_msg.content
                elif hasattr(last_msg, "text"):
                    output = last_msg.text
                else:
                    output = str(last_msg)
            else:
                output = "No response generated"

        return AgentResponse(
            output=output,
            state=result,
        )

    except Exception as e:
        # Log the full error for debugging
        import logging

        logger = logging.getLogger(__name__)
        logger.error(f"Agent error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Agent error: {str(e)}")


@router.post("/test-llm")
async def test_llm(request: LLMRequest):
    """Test the LLM directly without agent/tools.

    Args:
        request: The test request containing message and optional system prompt

    Returns:
        The LLM's direct response
    """
    if not settings.llm_api_key:
        raise HTTPException(
            status_code=500,
            detail="LLM API key not configured. Please set LLM_API_KEY environment variable.",
        )

    try:
        # Create LLM instance with default configuration
        llm_config = LLMConfig(vendor=settings.llm_vendor, model=settings.llm_model)
        llm = create_llm(llm_config)

        # Prepare messages
        messages = [
            {"role": "system", "content": request.system_prompt},
            {"role": "user", "content": request.message},
        ]

        # Get response
        response = llm.invoke(messages)

        return {"response": response.content}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"LLM error: {str(e)}")

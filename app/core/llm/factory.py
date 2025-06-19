"""Factory for creating LLM instances based on configuration."""

from typing import Any

from langchain_community.chat_models import ChatOllama
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_groq import ChatGroq

from app.core.config import LLMVendor, settings


class LLMConfig:
    """Configuration for LLM instances."""

    def __init__(
        self,
        vendor: LLMVendor = settings.llm_vendor,
        model: str = settings.llm_model,
        temperature: float = 0.7,
        **kwargs: Any,
    ):
        self.vendor = vendor
        self.model = model
        self.temperature = temperature
        self.extra_kwargs = kwargs


def create_llm(config: LLMConfig) -> BaseChatModel:
    """Create an LLM instance based on the provided configuration.

    Args:
        config: LLM configuration

    Returns:
        A configured LLM instance

    Raises:
        ValueError: If the vendor is not supported or required API keys are missing
    """
    if config.vendor == LLMVendor.GROQ:
        if not settings.llm_api_key:
            raise ValueError("Groq API key not configured")
        return ChatGroq(
            model=config.model,
            temperature=config.temperature,
            api_key=settings.llm_api_key,
            **config.extra_kwargs,
        )

    elif config.vendor == LLMVendor.GOOGLE:
        if not settings.google_api_key:
            raise ValueError("Google API key not configured")
        return ChatGoogleGenerativeAI(
            model=config.model,
            temperature=config.temperature,
            google_api_key=settings.google_api_key,
            **config.extra_kwargs,
        )

    elif config.vendor == LLMVendor.OLLAMA:
        return ChatOllama(
            model=config.model,
            temperature=config.temperature,
            base_url=settings.ollama_base_url,
            **config.extra_kwargs,
        )

    raise ValueError(f"Unsupported LLM vendor: {config.vendor}")

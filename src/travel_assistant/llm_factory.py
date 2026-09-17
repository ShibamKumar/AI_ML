import socket
from urllib.parse import urlparse

from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import AIMessage
from langchain_ollama import ChatOllama
from langchain_openai import ChatOpenAI

from .config import settings


class OfflineFallbackChatModel:
    """Deterministic, template-based composer used when no LLM backend is reachable.

    This guarantees the application remains runnable end-to-end (RAG retrieval +
    MCP tool calls + structured composition) even without an OpenAI API key or a
    running local Ollama server. It performs no destination-fact invention: it
    simply organizes the KB context and MCP tool outputs that were already
    retrieved by the orchestrator.
    """

    def invoke(self, prompt: str) -> AIMessage:
        content = (
            "Note: No LLM backend (OpenAI API key or local Ollama) was reachable, "
            "so this is an offline structured composition of the retrieved data "
            "rather than a model-generated narrative.\n\n"
            f"{prompt.strip()}"
        )
        return AIMessage(content=content)


def _ollama_reachable(model_name: str) -> bool:
    try:
        parsed = urlparse("http://127.0.0.1:11434")
        with socket.create_connection((parsed.hostname, parsed.port), timeout=0.5):
            return True
    except OSError:
        return False


def get_chat_model() -> BaseChatModel | OfflineFallbackChatModel:
    if settings.openai_api_key:
        return ChatOpenAI(
            model=settings.openai_model,
            temperature=0.2,
            api_key=settings.openai_api_key,
        )

    if _ollama_reachable(settings.ollama_model):
        return ChatOllama(model=settings.ollama_model, temperature=0.2)

    return OfflineFallbackChatModel()

from dataclasses import dataclass

from langchain_core.documents import Document

from .intent import (
    classify_intent,
    extract_currency_request,
    extract_days,
    has_currency_signal,
    has_weather_signal,
)
from .llm_factory import OfflineFallbackChatModel, get_chat_model
from .mcp_client import call_tool, get_mcp_tools
from .rag import get_retriever


@dataclass
class AssistantResponse:
    answer: str
    sources: list[dict]
    tool_outputs: list[dict]


def _format_docs(docs: list[Document]) -> tuple[str, list[dict]]:
    context_blocks: list[str] = []
    sources: list[dict] = []

    for idx, doc in enumerate(docs, start=1):
        title = doc.metadata.get("title", "Unknown source")
        url = doc.metadata.get("url", "N/A")
        snippet = doc.page_content.strip().replace("\n", " ")
        context_blocks.append(f"[{idx}] {snippet}")
        sources.append({"title": title, "url": url})

    return "\n\n".join(context_blocks), sources


def generate_response(
    user_query: str,
    chat_history: list[dict],
    include_evidence_in_answer: bool = False,
) -> AssistantResponse:
    intent = classify_intent(user_query)
    retrieved_docs: list[Document] = []
    try:
        retriever = get_retriever(k=4)
        retrieved_docs = retriever.invoke(user_query)
    except Exception:
        retrieved_docs = []
    kb_context, sources = _format_docs(retrieved_docs)

    tool_outputs: list[dict] = []
    tools = None

    if has_weather_signal(user_query):
        days = extract_days(user_query, default_days=3)
        try:
            tools = tools or get_mcp_tools()
            weather_data = call_tool(
                tools,
                "get_weather_forecast",
                {"city": "Singapore", "days": days},
            )
            tool_outputs.append(
                {"tool": "weather", "data": weather_data, "note": "Current information from MCP tool"}
            )
        except Exception as error:
            tool_outputs.append(
                {
                    "tool": "weather",
                    "data": f"Weather tool unavailable: {error}",
                    "note": "Tool failure",
                }
            )

    if has_currency_signal(user_query):
        parsed = extract_currency_request(user_query)
        if not parsed:
            tool_outputs.append(
                {
                    "tool": "currency",
                    "data": "Could not parse currency request. Please specify amount and two currency codes (e.g., INR 50000 to SGD).",
                    "note": "Input parsing warning",
                }
            )
        else:
            amount, from_currency, to_currency = parsed
            try:
                tools = tools or get_mcp_tools()
                currency_data = call_tool(
                    tools,
                    "convert_currency",
                    {
                        "amount": amount,
                        "from_currency": from_currency,
                        "to_currency": to_currency,
                    },
                )
                tool_outputs.append(
                    {"tool": "currency", "data": currency_data, "note": "Current information from MCP tool"}
                )
            except Exception as error:
                tool_outputs.append(
                    {
                        "tool": "currency",
                        "data": f"Currency tool unavailable: {error}",
                        "note": "Tool failure",
                    }
                )

    history_text = "\n".join(
        [f"{msg.get('role', 'user')}: {msg.get('content', '')}" for msg in chat_history[-8:]]
    )

    format_instruction = (
        "Provide a clean, user-facing answer only. Do NOT include labels like (A)/(B)/(C), do NOT include source indices, and do NOT include raw tool payloads. "
        "When weather is used, naturally mention forecast-driven adjustments in the itinerary."
        if not include_evidence_in_answer
        else "Distinguish sections: (A) Knowledge-base facts, (B) MCP current information, (C) Suggested plan."
    )

    prompt = f"""
You are an AI Travel Planning Assistant.

Rules:
1) Use only the provided knowledge base context for destination facts.
2) Use MCP tool outputs for current information (weather/currency).
3) If information is missing, explicitly say what is missing.
4) {format_instruction}
5) Cite source titles and URLs for knowledge-base facts.
6) Keep recommendations structured and day-wise when itinerary planning is requested.
7) Keep user preferences from chat history when relevant.

Chat history:
{history_text}

User question:
{user_query}

Knowledge-base context:
{kb_context if kb_context else 'No relevant KB context found. State clearly that destination details are unavailable.'}

MCP outputs:
{tool_outputs if tool_outputs else 'No MCP output used.'}

Now generate the final response.
"""

    llm = get_chat_model()
    try:
        answer = llm.invoke(prompt).content
    except Exception as error:
        fallback = OfflineFallbackChatModel()
        fallback_answer = fallback.invoke(prompt).content
        answer = (
            f"{fallback_answer}\n\n"
            f"[System note] Primary model invocation failed and offline fallback was used: {error}"
        )
    return AssistantResponse(answer=answer, sources=sources, tool_outputs=tool_outputs)

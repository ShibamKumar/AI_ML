import sys
from pathlib import Path
import ast
import json

import streamlit as st

ROOT = Path(__file__).resolve().parent
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from travel_assistant.orchestrator import generate_response
from travel_assistant.rag import build_or_load_vectorstore, load_kb_documents


def _deduplicate_sources(sources: list[dict]) -> list[dict]:
    unique: list[dict] = []
    seen: set[tuple[str, str]] = set()
    for source in sources:
        title = str(source.get("title", "Unknown source"))
        url = str(source.get("url", "N/A"))
        key = (title, url)
        if key in seen:
            continue
        seen.add(key)
        unique.append({"title": title, "url": url})
    return unique


def _extract_tool_payload(raw_data: object) -> object:
    if isinstance(raw_data, (dict, list)):
        return raw_data

    if not isinstance(raw_data, str):
        return raw_data

    parsed: object = raw_data
    try:
        parsed = json.loads(raw_data)
    except Exception:
        try:
            parsed = ast.literal_eval(raw_data)
        except Exception:
            return raw_data

    if isinstance(parsed, list) and parsed:
        first = parsed[0]
        if isinstance(first, dict) and "text" in first:
            text_value = first.get("text")
            if isinstance(text_value, str):
                try:
                    return json.loads(text_value)
                except Exception:
                    return text_value
    return parsed

st.set_page_config(page_title="AI Travel Planning Assistant", page_icon="✈️", layout="wide")
st.title("AI Travel Planning Assistant")
st.caption("RAG + MCP weather/currency integration for destination planning")

DEMO_PROMPTS = [
    "What are the must-visit attractions in Singapore?",
    "What is the weather forecast in Singapore for the next 3 days?",
    "Convert INR 50000 to SGD.",
    "Plan a 3-day Singapore itinerary for next week and adjust by weather",
    "I have INR 60000. Convert to SGD and suggest a 3-day itinerary.",
    "Make the plan family-friendly and reduce walking distance.",
]

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

with st.sidebar:
    st.subheader("Setup")
    if st.button("Build / Rebuild Knowledge Index"):
        docs = load_kb_documents()
        if not docs:
            st.error("No KB documents found in src/travel_assistant/kb")
        else:
            build_or_load_vectorstore(rebuild=True)
            st.success("Knowledge index built successfully.")
    if st.button("Clear chat"):
        st.session_state.chat_history = []
        st.rerun()

    st.subheader("Display")
    show_evidence_panels = st.checkbox(
        "Show sources and MCP output panels",
        value=False,
        help="Enable this for assignment review/debugging. Keep off for cleaner user-facing chat.",
    )

st.markdown("Ask destination, weather, currency, or combined planning questions.")
with st.expander("Demo quick prompts", expanded=False):
    selected_prompt = st.selectbox(
        "Choose a prompt",
        options=DEMO_PROMPTS,
        index=3,
        label_visibility="collapsed",
    )
    run_selected_prompt = st.button("Run selected prompt")

for msg in st.session_state.chat_history:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

query = st.chat_input("Example: Plan a 3-day Singapore itinerary for next week and adjust by weather")
if run_selected_prompt:
    query = selected_prompt

if query:
    st.session_state.chat_history.append({"role": "user", "content": query})
    with st.chat_message("user"):
        st.write(query)

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            response = generate_response(
                query,
                st.session_state.chat_history,
                include_evidence_in_answer=show_evidence_panels,
            )
            st.write(response.answer)

            if show_evidence_panels and response.sources:
                st.markdown("**Knowledge sources used**")
                for source in _deduplicate_sources(response.sources):
                    st.write(f"- {source['title']} — {source['url']}")

            if show_evidence_panels and response.tool_outputs:
                st.markdown("**MCP tool outputs used**")
                for output in response.tool_outputs:
                    tool_name = output.get("tool", "unknown")
                    note = output.get("note", "")
                    st.write(f"- {tool_name}{f' ({note})' if note else ''}")
                    normalized_data = _extract_tool_payload(output.get("data"))
                    if isinstance(normalized_data, (dict, list)):
                        st.json(normalized_data)
                    else:
                        st.write(normalized_data)

    st.session_state.chat_history.append({"role": "assistant", "content": response.answer})

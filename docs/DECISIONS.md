# Engineering Decisions

## 1) Destination Scope = Singapore
**Why**: Assignment recommendation, abundant public sources, and broad itinerary coverage.

## 2) RAG Stack = LangChain + Chroma + sentence-transformers
**Why**: Meets mandatory stack requirements with local-friendly embedding options and persistent vector storage.

## 3) Knowledge Base Format = Markdown with front-matter metadata
**Why**: Human-readable, easy to version control, and supports source citations in generated responses.

## 4) MCP Tools implemented as local FastMCP servers
**Why**: Strictly satisfies MCP integration requirement and keeps tool behavior testable and explicit.

- Weather tool provider: Open-Meteo (forecast)
- Currency tool provider: Frankfurter (conversion)

## 5) Intent-based tool routing before LLM response generation
**Why**: Predictable tool selection and clear separation of retrieval/tool phases from answer synthesis.

## 6) Prompt strategy
Prompt explicitly enforces:
- Use KB for destination facts
- Use MCP for current information
- Distinguish KB facts vs MCP facts vs model suggestions
- Declare missing information when needed
- Keep multi-turn context from recent conversation turns

## 7) Multi-turn context retention
Recent turn history is appended to prompt so follow-up preferences (family trip, pace, weather concerns) remain active.

## 8) Simplicity-first UI
Streamlit chosen for fast demonstration quality and assignment focus on AI workflow rather than front-end complexity.

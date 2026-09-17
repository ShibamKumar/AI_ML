# Architecture

## High-level Flow

1. User asks a question in Streamlit UI.
2. Intent router classifies request as destination, weather, currency, or combined.
3. Destination/combined queries trigger RAG retrieval from Chroma vector store.
4. Weather/currency/combined queries trigger MCP tool calls.
5. Prompt merges chat history, retrieved KB context, and MCP outputs.
6. LLM generates a structured response with source references and clear attribution.

## Components

- **UI layer**: `app.py`
- **Orchestration layer**: `src/travel_assistant/orchestrator.py`
- **RAG layer**: `src/travel_assistant/rag.py`
- **MCP integration layer**: `src/travel_assistant/mcp_client.py`
- **MCP tool servers**: `src/travel_assistant/mcp_servers/weather_server.py`, `currency_server.py`
- **Knowledge base**: `src/travel_assistant/kb/*.md`

## Data Contracts

### KB Document Metadata
- `title`
- `url`
- `source_type`

### MCP Tool Output
- Weather: city, day-wise forecast fields, provider
- Currency: input currencies/amount, converted amount, date, provider

## Failure Handling

- If KB retrieval is weak, assistant indicates insufficient destination data.
- If an MCP tool fails or returns unavailable data, assistant reports failure explicitly.
- No fabricated destination facts or current values.

# AI Travel Planning Assistant (RAG + MCP)

This project implements the **AI Travel Planning Assistant** assignment using:
- **RAG** for destination knowledge (Singapore)
- **MCP tools** for current weather and currency conversion
- **LangChain orchestration** with a simple **Streamlit** interface

## Features

- Destination assistant grounded in a document knowledge base
- Source-referenced answers (title + URL)
- MCP Weather tool integration (Open-Meteo via local MCP server)
- MCP Currency tool integration (Frankfurter API via local MCP server)
- Combined RAG + MCP responses for weather-aware itinerary and budget scenarios
- Multi-turn chat with conversation context retention
- Graceful handling when KB context is insufficient or tools fail

## Project Structure

- `app.py` — Streamlit UI
- `src/travel_assistant/rag.py` — document loading, chunking, embeddings, vector store
- `src/travel_assistant/mcp_servers/` — weather and currency MCP servers
- `src/travel_assistant/mcp_client.py` — MCP client and tool invocation
- `src/travel_assistant/orchestrator.py` — intent routing + response composition
- `src/travel_assistant/kb/` — curated destination knowledge docs with metadata
- `docs/` — architecture, decisions, checklist, sample QA, demo script

## Setup

1. Create and activate a Python environment (a `.venv` is recommended):
   ```bash
   python -m venv .venv
   .venv\Scripts\activate
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Copy `.env.example` to `.env`.
4. Optional (OpenAI): set `OPENAI_API_KEY` and model in `.env`.
   - If no API key is set, the app tries a local Ollama server (`OLLAMA_MODEL`).
   - If neither is available, the app uses a deterministic **offline fallback
     composer** so RAG retrieval and MCP tool integration remain fully
     demonstrable even without any LLM configured. Configure a real LLM for
     natural-language generation quality.

## Run

1. Build vector index:
   ```bash
   python scripts/build_index.py
   ```

2. Launch app:
   ```bash
   streamlit run app.py
   ```

The app was verified to build the index, call both MCP tools (Open-Meteo
weather, Frankfurter currency conversion), retrieve grounded KB context, and
start successfully in this workspace.

## Prompt & Context Strategy

The assistant prompt enforces:
- KB context for destination facts
- MCP outputs for current information
- explicit missing-information statements
- structured sections: KB facts, MCP current info, suggested plan
- source citations
- use of recent chat turns for preference continuity

See `docs/DECISIONS.md` for full rationale.

## Knowledge Base Sources

The knowledge base includes paraphrased notes grounded in:
1. Wikivoyage Singapore Travel Guide — https://en.wikivoyage.org/wiki/Singapore
2. Visit Singapore travel guide tips — https://www.visitsingapore.com/travel-guide-tips/
3. Visit Singapore things to do / itinerary references — https://www.visitsingapore.com/see-do-singapore/

## Sample Questions

See `docs/SAMPLE_QA.md` for evaluation prompts and expected response patterns.

## Assignment Deliverable Mapping

See `docs/SUBMISSION_CHECKLIST.md` for a direct mapping to acceptance criteria and deliverables.
# AI_ML

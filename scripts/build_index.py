import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from travel_assistant.rag import build_or_load_vectorstore, load_kb_documents


def main() -> None:
    docs = load_kb_documents()
    if not docs:
        raise SystemExit("No documents found in src/travel_assistant/kb")

    build_or_load_vectorstore(rebuild=True)
    print(f"Indexed {len(docs)} knowledge-base documents successfully.")


if __name__ == "__main__":
    main()

from pathlib import Path
from typing import Iterable

import yaml
from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

from .config import settings


def _parse_markdown_with_metadata(path: Path) -> Document:
    text = path.read_text(encoding="utf-8")
    metadata: dict = {}
    content = text

    if text.startswith("---"):
        parts = text.split("---", 2)
        if len(parts) == 3:
            metadata_block = parts[1]
            content = parts[2].strip()
            metadata = yaml.safe_load(metadata_block) or {}

    metadata["source_file"] = str(path)
    metadata.setdefault("title", path.stem)
    metadata.setdefault("url", "N/A")
    return Document(page_content=content, metadata=metadata)


def load_kb_documents(kb_dir: str = "src/travel_assistant/kb") -> list[Document]:
    docs: list[Document] = []
    for path in sorted(Path(kb_dir).glob("*.md")):
        docs.append(_parse_markdown_with_metadata(path))
    return docs


def _chunk_documents(documents: Iterable[Document]) -> list[Document]:
    splitter = RecursiveCharacterTextSplitter(chunk_size=800, chunk_overlap=120)
    return splitter.split_documents(list(documents))


def build_or_load_vectorstore(rebuild: bool = False) -> Chroma:
    settings.chroma_path.mkdir(parents=True, exist_ok=True)
    embeddings = HuggingFaceEmbeddings(model_name=settings.embedding_model)

    if rebuild:
        documents = load_kb_documents()
        chunks = _chunk_documents(documents)
        return Chroma.from_documents(
            documents=chunks,
            embedding=embeddings,
            persist_directory=str(settings.chroma_path),
            collection_name="travel_kb",
        )

    return Chroma(
        persist_directory=str(settings.chroma_path),
        embedding_function=embeddings,
        collection_name="travel_kb",
    )


def get_retriever(k: int = 4):
    vectorstore = build_or_load_vectorstore(rebuild=False)
    return vectorstore.as_retriever(search_kwargs={"k": k})

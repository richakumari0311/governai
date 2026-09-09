import chromadb
from src.rag.chunking import Chunk
from src.rag.embeddings import embed_texts

CHROMA_PATH = "chroma_db"


def get_collection(name: str):
    """Create or fetch a persistent ChromaDB collection stored on disk at CHROMA_PATH."""
    client = chromadb.PersistentClient(path=CHROMA_PATH)
    return client.get_or_create_collection(name=name)


def add_chunks(collection, chunks: list[Chunk]) -> None:
    """Embed a list of Chunks and add them to the given ChromaDB collection."""
    if not chunks:
        return

    texts = [c.text for c in chunks]
    embeddings = embed_texts(texts)

    ids = [f"{c.source}_{i}" for i, c in enumerate(chunks)]
    metadatas = [{"source": c.source, "chunk_type": c.chunk_type} for c in chunks]

    collection.add(
        ids=ids,
        embeddings=embeddings,
        documents=texts,
        metadatas=metadatas,
    )


def query_collection(collection, query_text: str, n_results: int = 5, where: dict | None = None):
    """Embed a query and return the n_results nearest chunks, optionally filtered by metadata."""
    query_embedding = embed_texts([query_text])[0]
    kwargs = {"query_embeddings": [query_embedding], "n_results": n_results}
    if where:
        kwargs["where"] = where
    return collection.query(**kwargs)
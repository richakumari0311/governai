from pathlib import Path
from src.rag.chunking import chunk_document
from src.rag.store import get_collection, add_chunks, query_collection

CORPUS_DIR = Path("data/corpus")

DOCS = [
    {"file": "hr_leave_policy.md", "title": "HR Leave Policy"},
    {"file": "finance_reimbursement_policy.md", "title": "Finance Reimbursement Policy"},
    {"file": "support_it_policy.md", "title": "Support IT Policy"},
]


def ingest_all():
    collection = get_collection("governai")

    for doc in DOCS:
        path = CORPUS_DIR / doc["file"]
        text = path.read_text()
        chunks = chunk_document(text, doc_title=doc["title"], source=doc["file"])
        add_chunks(collection, chunks)
        print(f"ingested {len(chunks)} chunks from {doc['file']}")

    return collection


if __name__ == "__main__":
    collection = ingest_all()

    results = query_collection(collection, "how many leave days does a Manager get")
    print("\n--- query results ---")
    for doc, meta in zip(results["documents"][0], results["metadatas"][0]):
        print(f"[{meta['chunk_type']} | {meta['source']}] {doc}")
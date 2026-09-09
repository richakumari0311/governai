from src.rag.chunking import chunk_document

with open("data/corpus/finance_reimbursement_policy.md") as f:
    text = f.read()

chunks = chunk_document(text, doc_title="Finance Reimbursement Policy", source="finance_reimbursement_policy.md")

for i, chunk in enumerate(chunks):
    print(f"--- Chunk {i} [{chunk.chunk_type}] ---")
    print(chunk.text)
    print()
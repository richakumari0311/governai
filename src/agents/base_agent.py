from google import genai
from google.genai import types
from src.config import settings
from src.rag.store import get_collection, query_collection

client = genai.Client(api_key=settings.gemini_api_key)


def make_domain_agent(domain_name: str, allowed_sources: list[str]):
    """Factory that returns an answer function scoped to one domain's documents."""

    system_instruction = f"""You are a {domain_name} policy assistant. Answer the
user's question using ONLY the information in the provided context. If the context
does not contain enough information to answer confidently, say so explicitly rather
than guessing. Do not use any outside knowledge. Cite which source document each
fact comes from."""

    def answer_question(question: str, n_results: int = 5) -> dict:
        collection = get_collection("governai")
        results = query_collection(collection, question, n_results=n_results)

        retrieved_chunks = results["documents"][0]
        retrieved_sources = [m["source"] for m in results["metadatas"][0]]

        context = "\n\n".join(
            f"[Source: {src}]\n{chunk}"
            for src, chunk in zip(retrieved_sources, retrieved_chunks)
        )

        prompt = f"Context:\n{context}\n\nQuestion: {question}"

        response = client.models.generate_content(
            model="gemini-3.6-flash",
            contents=prompt,
            config=types.GenerateContentConfig(system_instruction=system_instruction),
        )

        return {
            "answer": response.text,
            "retrieved_chunks": retrieved_chunks,
            "sources": list(set(retrieved_sources)),
            "domain": domain_name,
        }

    return answer_question
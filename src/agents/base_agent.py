from google import genai
from google.genai import types
from tenacity import retry, wait_exponential, stop_after_attempt
from src.config import settings
from src.rag.store import get_collection, query_collection

client = genai.Client(api_key=settings.gemini_api_key)


@retry(wait=wait_exponential(multiplier=2, min=15, max=90), stop=stop_after_attempt(5))
def _generate(model: str, prompt: str, system_instruction: str):
    return client.models.generate_content(
        model=model,
        contents=prompt,
        config=types.GenerateContentConfig(system_instruction=system_instruction),
    )


def make_domain_agent(domain_name: str, allowed_sources: list[str]):
    """Factory that returns an answer function scoped to one domain's documents."""

    system_instruction = f"""You are a {domain_name} policy assistant. Answer the
user's question using ONLY the information in the provided context. If the context
does not contain enough information to answer confidently, say so explicitly rather
than guessing. Do not use any outside knowledge. Cite which source document each
fact comes from."""

    where_filter = {"source": {"$in": allowed_sources}}

    def answer_question(question: str, n_results: int = 5) -> dict:
        collection = get_collection("governai")
        results = query_collection(collection, question, n_results=n_results, where=where_filter)

        retrieved_chunks = results["documents"][0]
        retrieved_sources = [m["source"] for m in results["metadatas"][0]]

        context = "\n\n".join(
            f"[Source: {src}]\n{chunk}"
            for src, chunk in zip(retrieved_sources, retrieved_chunks)
        )

        prompt = f"Context:\n{context}\n\nQuestion: {question}"

        response = _generate("gemini-3.5-flash-lite", prompt, system_instruction)

        return {
            "answer": response.text,
            "retrieved_chunks": retrieved_chunks,
            "sources": list(set(retrieved_sources)),
            "domain": domain_name,
        }

    return answer_question
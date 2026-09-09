import json
from google import genai
from google.genai import types
from tenacity import retry, wait_exponential, stop_after_attempt
from src.config import settings

client = genai.Client(api_key=settings.gemini_api_key)

ROUTER_INSTRUCTION = """You are a routing classifier for an enterprise assistant with
three domains: HR, Finance, and Support. Given a user question, output a confidence
score from 0 to 1 for each domain, reflecting how relevant that domain is to
answering the question. A question can be relevant to multiple domains if it
genuinely spans them. Respond ONLY with valid JSON in this exact format, no other
text: {"HR": 0.0, "Finance": 0.0, "Support": 0.0}"""


@retry(wait=wait_exponential(multiplier=2, min=15, max=90), stop=stop_after_attempt(5))
def classify_query(question: str) -> dict:
    """Return a relevance score per domain for the given question."""
    response = client.models.generate_content(
        model="gemini-3.5-flash-lite",
        contents=question,
        config=types.GenerateContentConfig(
            system_instruction=ROUTER_INSTRUCTION,
            response_mime_type="application/json",
        ),
    )
    return json.loads(response.text)


def route_domains(question: str, threshold: float = 0.35) -> list[str]:
    """Return the list of domains relevant to this question, above threshold."""
    scores = classify_query(question)
    selected = [domain for domain, score in scores.items() if score >= threshold]

    if not selected:
        selected = [max(scores, key=scores.get)]

    return selected
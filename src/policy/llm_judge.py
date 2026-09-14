import json
from google import genai
from google.genai import types
from tenacity import retry, wait_exponential, stop_after_attempt
from src.config import settings

client = genai.Client(api_key=settings.gemini_api_key)

JUDGE_INSTRUCTION = """You are a policy compliance judge for an enterprise system.
Given a policy context and a situation to evaluate, determine whether the situation
complies with the stated policy. If the policy context does not explicitly define a
rule or limit covering this exact situation, you must treat this as ambiguous — do
NOT assume compliance just because no rule was violated. In that case, set confidence
low (below 0.5) to reflect genuine uncertainty, rather than confidently approving.
Respond ONLY with valid JSON in this exact format, no other text:
{"compliant": true/false, "confidence": 0.0, "reasoning": "..."}
"confidence" reflects how certain you are given the information available."""

@retry(wait=wait_exponential(multiplier=2, min=15, max=90), stop=stop_after_attempt(5))
def judge_compliance(policy_context: str, situation: str) -> dict:
    """Ask the LLM to judge whether a situation complies with the given policy context."""
    prompt = f"Policy context:\n{policy_context}\n\nSituation to evaluate:\n{situation}"

    response = client.models.generate_content(
        model="gemini-3.5-flash-lite",
        contents=prompt,
        config=types.GenerateContentConfig(
            system_instruction=JUDGE_INSTRUCTION,
            response_mime_type="application/json",
        ),
    )
    return json.loads(response.text)
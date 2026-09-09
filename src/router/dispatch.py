from src.router.router import route_domains
from src.agents.agents import answer_hr_question, answer_finance_question, answer_support_question

AGENT_MAP = {
    "HR": answer_hr_question,
    "Finance": answer_finance_question,
    "Support": answer_support_question,
}


def answer_question(question: str) -> dict:
    """Route a question to the relevant domain agent(s) and merge if more than one."""
    domains = route_domains(question)
    results = [AGENT_MAP[domain](question) for domain in domains]

    if len(results) == 1:
        return results[0]

    merged_answer = "\n\n".join(f"[{r['domain']}]\n{r['answer']}" for r in results)
    merged_sources = list({s for r in results for s in r["sources"]})
    merged_chunks = [c for r in results for c in r["retrieved_chunks"]]

    return {
        "answer": merged_answer,
        "retrieved_chunks": merged_chunks,
        "sources": merged_sources,
        "domain": domains,
    }
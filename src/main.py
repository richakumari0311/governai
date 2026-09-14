from fastapi import FastAPI
from pydantic import BaseModel
from src.graph.build import build_graph

app = FastAPI(title="Enterprise Copilot", description="Governed multi-agent enterprise assistant")
graph = build_graph()


class PolicyCheckInput(BaseModel):
    rule_id: str | None = None
    level: str | None = None
    value: float | None = None
    policy_context: str = ""
    situation: str = ""


class QuestionRequest(BaseModel):
    question: str
    policy_check: PolicyCheckInput | None = None


class QuestionResponse(BaseModel):
    answer: str
    sources: list[str]
    domains: list[str]
    decision: dict


@app.post("/ask", response_model=QuestionResponse)
def ask(request: QuestionRequest):
    policy_check_dict = request.policy_check.model_dump() if request.policy_check else None

    result = graph.invoke({
        "question": request.question,
        "policy_check": policy_check_dict,
    })

    agent_result = result["agent_result"]
    domains = agent_result["domain"] if isinstance(agent_result["domain"], list) else [agent_result["domain"]]

    return QuestionResponse(
        answer=agent_result["answer"],
        sources=agent_result["sources"],
        domains=domains,
        decision=result["decision_result"],
    )


@app.get("/health")
def health():
    return {"status": "ok"}
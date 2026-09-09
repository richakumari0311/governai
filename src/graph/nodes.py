from src.router.dispatch import answer_question
from src.policy.policy_engine import check_policy
from src.policy.decision import decide_action
from src.audit.store import log_interaction


def route_and_answer(state: dict) -> dict:
    """Node: send the question through the router to the relevant agent(s)."""
    result = answer_question(state["question"])
    return {"agent_result": result}


def run_policy_check(state: dict) -> dict:
    """Node: run the policy engine using the caller-supplied policy_check spec."""
    pc = state["policy_check"]
    result = check_policy(
        rule_id=pc.get("rule_id"),
        level=pc.get("level"),
        value=pc.get("value"),
        policy_context=pc.get("policy_context", ""),
        situation=pc.get("situation", ""),
    )
    return {"policy_result": result}


def make_decision(state: dict) -> dict:
    """Node: decide auto_approve/auto_reject/human_approval based on policy_result, if any."""
    policy_result = state.get("policy_result")
    if policy_result is None:
        decision = {"action": "auto_approve", "confidence": 1.0}
    else:
        decision = decide_action(policy_result)
    return {"decision_result": decision}


def write_audit_log(state: dict) -> dict:
    """Node: log the completed interaction. Terminal node — no new state needed."""
    agent_result = state["agent_result"]
    domains = agent_result["domain"] if isinstance(agent_result["domain"], list) else [agent_result["domain"]]

    log_interaction(
        question=state["question"],
        domains=domains,
        answer=agent_result["answer"],
        policy_result=state.get("policy_result"),
        decision_result=state["decision_result"],
    )
    return {}
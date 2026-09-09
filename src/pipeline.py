from src.router.dispatch import answer_question
from src.policy.policy_engine import check_policy
from src.policy.decision import decide_action
from src.audit.store import log_interaction


def process_question(
    question: str,
    policy_check: dict | None = None,
) -> dict:
    """
    Full pipeline: route question to agent(s), optionally run a policy check,
    decide the action, log the interaction, and return the combined result.

    policy_check, if provided, should be a dict with keys:
      rule_id, level, value, policy_context, situation
    """
    agent_result = answer_question(question)

    policy_result = None
    decision_result = {"action": "auto_approve", "confidence": 1.0}  # default: no policy check needed

    if policy_check:
        policy_result = check_policy(
            rule_id=policy_check.get("rule_id"),
            level=policy_check.get("level"),
            value=policy_check.get("value"),
            policy_context=policy_check.get("policy_context", ""),
            situation=policy_check.get("situation", ""),
        )
        decision_result = decide_action(policy_result)

    domains = agent_result["domain"] if isinstance(agent_result["domain"], list) else [agent_result["domain"]]

    log_interaction(
        question=question,
        domains=domains,
        answer=agent_result["answer"],
        policy_result=policy_result,
        decision_result=decision_result,
    )

    return {
        "answer": agent_result["answer"],
        "sources": agent_result["sources"],
        "domains": domains,
        "policy_result": policy_result,
        "decision": decision_result,
    }
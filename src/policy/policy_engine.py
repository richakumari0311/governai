from src.policy.rule_engine import find_rule, evaluate_numeric_max
from src.policy.llm_judge import judge_compliance


def check_policy(rule_id: str | None, level: str | None, value: float | None, policy_context: str, situation: str) -> dict:
    """Check compliance: try the matching rule first, fall back to LLM judgment."""
    if rule_id:
        rule = find_rule(rule_id)
        if rule and level is not None and value is not None:
            result = evaluate_numeric_max(rule, level, value)
            if result["compliant"] is not None:
                result["method"] = "rule"
                result["confidence"] = 1.0
                return result

    judgment = judge_compliance(policy_context, situation)
    judgment["method"] = "llm_judge"
    judgment["rule_id"] = rule_id
    return judgment
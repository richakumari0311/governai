CONFIDENCE_THRESHOLD = 0.75


def decide_action(policy_result: dict, threshold: float = CONFIDENCE_THRESHOLD) -> dict:
    """Decide whether a policy result should be auto-resolved or escalated to a human."""
    confidence = policy_result.get("confidence", 0.0)
    compliant = policy_result.get("compliant")

    if confidence < threshold:
        action = "human_approval"
        reason = f"Confidence {confidence} below threshold {threshold} — escalating for human review"
    elif compliant is True:
        action = "auto_approve"
        reason = f"Confidence {confidence} meets threshold; policy check passed"
    elif compliant is False:
        action = "auto_reject"
        reason = f"Confidence {confidence} meets threshold; policy check failed"
    else:
        action = "human_approval"
        reason = "Compliance could not be determined — escalating for human review"

    return {
        "action": action,
        "reason": reason,
        "confidence": confidence,
        "compliant": compliant,
    }
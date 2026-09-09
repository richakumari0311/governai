from src.policy.decision import decide_action

# high confidence, compliant -> auto_approve
print(decide_action({"confidence": 1.0, "compliant": True}))

# high confidence, non-compliant -> auto_reject
print(decide_action({"confidence": 1.0, "compliant": False}))

# low confidence -> human_approval regardless of compliant
print(decide_action({"confidence": 0.5, "compliant": True}))
print(decide_action({"confidence": 0.5, "compliant": False}))

# undetermined -> human_approval
print(decide_action({"confidence": 0.9, "compliant": None}))
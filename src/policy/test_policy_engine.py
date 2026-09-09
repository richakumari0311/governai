from src.policy.policy_engine import check_policy

# should resolve via rule (Manager, travel, exceeds 1200)
print(check_policy("finance_travel_limit", "Manager", 1500, "", ""))

print()

# no rule_id given -> forces LLM judge
print(check_policy(
    None, None, None,
    policy_context="Employees must submit travel expense claims within 30 days of the expense date.",
    situation="An employee submitted a travel expense claim 45 days after the trip, with no explanation given."
))
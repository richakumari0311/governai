from src.policy.rule_engine import find_rule, evaluate_numeric_max

rule = find_rule("finance_travel_limit")

print(evaluate_numeric_max(rule, "Manager", 1500))  # expect compliant: False (exceeds 1200)
print(evaluate_numeric_max(rule, "Manager", 900))    # expect compliant: True
print(evaluate_numeric_max(rule, "Intern", 100))      # expect compliant: None (no limit defined)
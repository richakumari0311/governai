from src.pipeline import process_question

# informational only, no policy check
result = process_question("How many leave days does a Manager get?")
print("ANSWER:", result["answer"])
print("DECISION:", result["decision"])

print()

# with an explicit policy check attached
result = process_question(
    "Can I expense a $1500 flight as a Manager?",
    policy_check={"rule_id": "finance_travel_limit", "level": "Manager", "value": 1500},
)
print("ANSWER:", result["answer"])
print("DECISION:", result["decision"])
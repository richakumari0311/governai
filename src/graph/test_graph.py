from src.graph.build import build_graph

app = build_graph()

# no policy check
result = app.invoke({"question": "How many leave days does a Manager get?", "policy_check": None})
print("ANSWER:", result["agent_result"]["answer"])
print("DECISION:", result["decision_result"])

print()

# with policy check
result = app.invoke({
    "question": "Can I expense a $1500 flight as a Manager?",
    "policy_check": {"rule_id": "finance_travel_limit", "level": "Manager", "value": 1500},
})
print("ANSWER:", result["agent_result"]["answer"])
print("DECISION:", result["decision_result"])
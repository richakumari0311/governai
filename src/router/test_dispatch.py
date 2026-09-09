from src.router.dispatch import answer_question

# single-domain cases
print(answer_question("How many leave days does a Manager get?")["answer"])
print()
print(answer_question("What's the P1 escalation time?")["answer"])
print()

# the deliberately cross-domain case
result = answer_question("How do I expense a laptop I need for remote work?")
print("DOMAINS ROUTED:", result["domain"])
print(result["answer"])
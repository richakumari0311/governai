from src.agents.hr_agent import answer_hr_question

result = answer_hr_question("What's the company's stock option vesting schedule?")

print("ANSWER:")
print(result["answer"])
print("\nSOURCES:", result["sources"])
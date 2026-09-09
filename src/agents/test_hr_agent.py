from src.agents.agents import answer_hr_question, answer_finance_question, answer_support_question

print(answer_hr_question("How many leave days does a Manager get?")["answer"])
print()
print(answer_finance_question("What's the travel reimbursement limit for a Senior Manager?")["answer"])
print()
print(answer_support_question("How fast should a P1 ticket get a first response?")["answer"])
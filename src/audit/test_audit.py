from src.audit.store import init_audit_table, log_interaction

init_audit_table()

log_interaction(
    question="Can I expense a $1500 flight as a Manager?",
    domains=["Finance"],
    answer="No, the travel limit for a Manager is $1200 per trip.",
    policy_result={"method": "rule", "compliant": False},
    decision_result={"action": "auto_reject", "confidence": 1.0},
)

print("logged successfully")
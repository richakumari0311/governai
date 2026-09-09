from src.agents.base_agent import make_domain_agent

answer_hr_question = make_domain_agent(
    domain_name="HR",
    allowed_sources=["hr_leave_policy.md"],
)

answer_finance_question = make_domain_agent(
    domain_name="Finance",
    allowed_sources=["finance_reimbursement_policy.md"],
)

answer_support_question = make_domain_agent(
    domain_name="Support",
    allowed_sources=["support_it_policy.md"],
)
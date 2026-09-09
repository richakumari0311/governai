from src.audit.models import metadata, audit_log
from src.db import engine


def init_audit_table():
    """Create the audit_log table if it doesn't already exist."""
    metadata.create_all(engine, tables=[audit_log])


def log_interaction(
    question: str,
    domains: list[str],
    answer: str,
    policy_result: dict | None,
    decision_result: dict,
) -> None:
    """Insert one audit record for a completed question->answer->decision cycle."""
    with engine.connect() as conn:
        conn.execute(
            audit_log.insert().values(
                question=question,
                domains=",".join(domains),
                answer=answer,
                policy_method=policy_result.get("method") if policy_result else None,
                policy_compliant=str(policy_result.get("compliant")) if policy_result else None,
                confidence=decision_result.get("confidence"),
                action=decision_result["action"],
            )
        )
        conn.commit()
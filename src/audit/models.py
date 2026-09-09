from sqlalchemy import Table, Column, Integer, String, Text, DateTime, MetaData, Float
from sqlalchemy.sql import func

metadata = MetaData()

audit_log = Table(
    "audit_log",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("question", Text, nullable=False),
    Column("domains", String, nullable=False),          # comma-separated, e.g. "Finance,Support"
    Column("answer", Text, nullable=False),
    Column("policy_method", String, nullable=True),      # "rule" or "llm_judge" or None
    Column("policy_compliant", String, nullable=True),   # "True" / "False" / "None" as string
    Column("confidence", Float, nullable=True),
    Column("action", String, nullable=False),            # auto_approve / auto_reject / human_approval
    Column("created_at", DateTime, server_default=func.now()),
)
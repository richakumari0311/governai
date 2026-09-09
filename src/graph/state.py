from typing import TypedDict, Optional


class PipelineState(TypedDict):
    question: str
    policy_check: Optional[dict]
    agent_result: Optional[dict]
    policy_result: Optional[dict]
    decision_result: Optional[dict]
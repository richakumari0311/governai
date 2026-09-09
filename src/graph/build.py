from langgraph.graph import StateGraph, END
from src.graph.state import PipelineState
from src.graph.nodes import route_and_answer, run_policy_check, make_decision, write_audit_log


def needs_policy_check(state: dict) -> str:
    """Conditional edge: route to policy check only if the caller supplied one."""
    return "policy_check" if state.get("policy_check") else "skip_policy"


def build_graph():
    graph = StateGraph(PipelineState)

    graph.add_node("route_and_answer", route_and_answer)
    graph.add_node("run_policy_check", run_policy_check)
    graph.add_node("make_decision", make_decision)
    graph.add_node("write_audit_log", write_audit_log)

    graph.set_entry_point("route_and_answer")

    graph.add_conditional_edges(
        "route_and_answer",
        needs_policy_check,
        {
            "policy_check": "run_policy_check",
            "skip_policy": "make_decision",
        },
    )

    graph.add_edge("run_policy_check", "make_decision")
    graph.add_edge("make_decision", "write_audit_log")
    graph.add_edge("write_audit_log", END)

    return graph.compile()
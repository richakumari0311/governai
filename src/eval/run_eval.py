import yaml
import time
from pathlib import Path
from src.graph.build import build_graph

TEST_SET_PATH = Path("data/eval/test_set.yaml")

graph = build_graph()


def load_test_set() -> dict:
    with open(TEST_SET_PATH) as f:
        return yaml.safe_load(f)


def run_qa_eval(qa_cases: list[dict]) -> dict:
    """Run each QA case through the graph, score routing, retrieval, and groundedness."""
    routing_correct = 0
    retrieval_correct = 0
    groundedness_scores = []  # 1 = grounded/correctly declined, 0 = hallucinated
    latencies = []

    results = []

    for case in qa_cases:
        start = time.time()
        output = graph.invoke({"question": case["question"], "policy_check": None})
        elapsed = time.time() - start
        latencies.append(elapsed)

        agent_result = output["agent_result"]
        actual_domains = agent_result["domain"] if isinstance(agent_result["domain"], list) else [agent_result["domain"]]
        actual_sources = agent_result["sources"]

        # routing: did the actual domains match expected (as sets, order doesn't matter)
        routing_match = set(actual_domains) == set(case["expected_domain"])
        if routing_match:
            routing_correct += 1

        # retrieval: only scored for in-scope cases with a defined expected source
        retrieval_match = None
        if case["in_scope"] and case["expected_source"]:
            retrieval_match = case["expected_source"] in actual_sources
            if retrieval_match:
                retrieval_correct += 1

        # groundedness: split multi-domain answers on the "[Domain]" markers dispatch.py
        # inserts, and require EVERY sub-answer to decline for the whole thing to
        # count as "declined" — otherwise a partial real answer gets wrongly penalized
        decline_phrases = [
            "does not contain", "cannot answer", "no information",
            "not able to answer", "no mention of", "not mentioned",
            "does not provide", "cannot confirm", "unable to answer",
        ]

        sub_answers = [a.strip() for a in agent_result["answer"].split("\n\n[") if a.strip()]
        if len(sub_answers) <= 1:
            sub_answers = [agent_result["answer"]]

        declined_flags = [
            any(phrase in sa.lower() for phrase in decline_phrases)
            for sa in sub_answers
        ]
        declined = all(declined_flags)

        if case["in_scope"]:
            grounded = 1 if not declined else 0
        else:
            grounded = 1 if declined else 0
        groundedness_scores.append(grounded)

        results.append({
            "question": case["question"],
            "expected_domain": case["expected_domain"],
            "actual_domain": actual_domains,
            "routing_match": routing_match,
            "retrieval_match": retrieval_match,
            "grounded": bool(grounded),
            "declined": declined,
            "latency_sec": round(elapsed, 2),
        })

    n = len(qa_cases)
    n_retrieval_scored = sum(1 for c in qa_cases if c["in_scope"] and c["expected_source"])

    return {
        "routing_accuracy": routing_correct / n,
        "retrieval_accuracy": retrieval_correct / n_retrieval_scored if n_retrieval_scored else None,
        "groundedness": sum(groundedness_scores) / n,
        "hallucination_rate": 1 - (sum(groundedness_scores) / n),
        "avg_latency_sec": sum(latencies) / n,
        "details": results,
    }

def run_policy_eval(policy_cases: list[dict]) -> dict:
    """Run each policy case through check_policy + decide_action, score decision accuracy."""
    from src.policy.policy_engine import check_policy
    from src.policy.decision import decide_action

    correct = 0
    results = []

    for case in policy_cases:
        policy_result = check_policy(
            rule_id=case["rule_id"],
            level=case["level"],
            value=case["value"],
            policy_context=case.get("policy_context", ""),
            situation=case.get("situation", ""),
        )
        decision = decide_action(policy_result)

        match = decision["action"] == case["expected_action"]
        if match:
            correct += 1

        results.append({
            "description": case["description"],
            "expected_action": case["expected_action"],
            "actual_action": decision["action"],
            "match": match,
        })

    return {
        "policy_decision_accuracy": correct / len(policy_cases),
        "details": results,
    }


def main():
    test_set = load_test_set()

    print("Running QA eval...")
    qa_results = run_qa_eval(test_set["qa_cases"])

    print("Running policy eval...")
    policy_results = run_policy_eval(test_set["policy_cases"])

    print("\n=== RESULTS ===")
    print(f"Routing Accuracy:       {qa_results['routing_accuracy']:.0%}")
    print(f"Retrieval Accuracy:     {qa_results['retrieval_accuracy']:.0%}")
    print(f"Groundedness:           {qa_results['groundedness']:.0%}")
    print(f"Hallucination Rate:     {qa_results['hallucination_rate']:.0%}")
    print(f"Avg Latency:            {qa_results['avg_latency_sec']:.2f} sec")
    print(f"Policy Decision Acc.:   {policy_results['policy_decision_accuracy']:.0%}")

    print("\n=== QA CASE DETAILS ===")
    for r in qa_results["details"]:
        status = "OK" if r["routing_match"] and r["grounded"] else "FAIL"
        print(f"[{status}] {r['question']}")
        print(f"       expected={r['expected_domain']} actual={r['actual_domain']} grounded={r['grounded']} latency={r['latency_sec']}s")

    print("\n=== POLICY CASE DETAILS ===")
    for r in policy_results["details"]:
        status = "OK" if r["match"] else "FAIL"
        print(f"[{status}] {r['description']}: expected={r['expected_action']} actual={r['actual_action']}")


if __name__ == "__main__":
    main()
import yaml
from pathlib import Path

RULES_PATH = Path("src/policy/rules.yaml")


def load_rules() -> list[dict]:
    with open(RULES_PATH) as f:
        data = yaml.safe_load(f)
    return data["rules"]


def find_rule(rule_id: str) -> dict | None:
    for rule in load_rules():
        if rule["id"] == rule_id:
            return rule
    return None


def evaluate_numeric_max(rule: dict, level: str, value: float) -> dict:
    """Check whether value exceeds the limit defined for this level under this rule."""
    limit = rule["limits"].get(level)

    if limit is None:
        return {
            "rule_id": rule["id"],
            "compliant": None,
            "reason": f"No limit defined for level '{level}' under rule '{rule['id']}'",
        }

    compliant = value <= limit
    return {
        "rule_id": rule["id"],
        "compliant": compliant,
        "limit": limit,
        "value": value,
        "reason": f"{value} {'within' if compliant else 'exceeds'} limit of {limit} for {level}",
    }
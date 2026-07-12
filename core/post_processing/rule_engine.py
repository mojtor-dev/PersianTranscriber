import json
import re
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class CompiledRule:
    rule_id: str
    description: str
    category: str
    pattern: re.Pattern
    replacement: str
    enabled: bool = True


class PostProcessingRuleEngine:
    VALID_CATEGORIES = {"spacing", "punctuation", "orthography", "formatting"}

    def __init__(self, rules_path=None):
        root = Path(__file__).resolve().parents[2]
        self.rules_path = Path(rules_path).expanduser().resolve() if rules_path else root / "data" / "post_processing" / "safe_rules.json"
        self.rules = self._load_rules()

    def apply(self, text):
        if not isinstance(text, str):
            raise TypeError("text must be a string")

        result = text
        details = []
        total = 0

        for rule in self.rules:
            if not rule.enabled:
                continue
            result, count = rule.pattern.subn(rule.replacement, result)
            if count:
                total += count
                details.append({
                    "rule_id": rule.rule_id,
                    "description": rule.description,
                    "category": rule.category,
                    "count": count,
                })

        return result, {
            "replacement_count": total,
            "matched_rules": len(details),
            "details": details,
        }

    def _load_rules(self):
        if not self.rules_path.is_file():
            return []

        payload = json.loads(self.rules_path.read_text(encoding="utf-8"))
        raw_rules = payload.get("rules")
        if not isinstance(raw_rules, list):
            raise ValueError("rules JSON must contain a rules list")

        compiled = []
        seen = set()

        for item in raw_rules:
            required = {"id", "description", "category", "pattern", "replacement"}
            missing = required - item.keys()
            if missing:
                raise ValueError("rule missing fields: " + ", ".join(sorted(missing)))
            if item["id"] in seen:
                raise ValueError(f"duplicate rule id: {item['id']}")
            if item["category"] not in self.VALID_CATEGORIES:
                raise ValueError(f"invalid category: {item['category']}")
            seen.add(item["id"])
            compiled.append(CompiledRule(
                rule_id=item["id"],
                description=item["description"],
                category=item["category"],
                pattern=re.compile(item["pattern"]),
                replacement=item["replacement"],
                enabled=item.get("enabled", True),
            ))

        return compiled

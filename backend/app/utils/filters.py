import re
from typing import List, Tuple, Optional
from ..schemas.context import FilterSet

# Default filter rules
DEFAULT_FILTERS = [
    r"(?i)kill|murder|suicide|self-harm",
    r"(?i)hate|racist|sexist|homophobic",
    r"(?i)illegal|drugs|weapons",
    r"(?i)explicit|porn|nude",
    r"(?i)scam|fraud|phishing"
]

class PromptFilter:
    def __init__(self, filter_set: Optional[FilterSet] = None):
        self.filter_set = filter_set or FilterSet(
            name="default",
            rules=DEFAULT_FILTERS,
            is_default=True
        )
        self.compiled_rules = [re.compile(rule) for rule in self.filter_set.rules]

    def check_prompt(self, prompt: str) -> Tuple[bool, List[str]]:
        """
        Check if a prompt violates any filter rules.
        Returns (is_safe, list_of_violations)
        """
        violations = []
        for rule in self.compiled_rules:
            if rule.search(prompt):
                violations.append(rule.pattern)
        
        return len(violations) == 0, violations

    def update_filters(self, new_filters: FilterSet):
        """Update the filter set with new rules"""
        self.filter_set = new_filters
        self.compiled_rules = [re.compile(rule) for rule in self.filter_set.rules]

    def get_filter_summary(self) -> dict:
        """Get a summary of current filter rules"""
        return {
            "name": self.filter_set.name,
            "description": self.filter_set.description,
            "rule_count": len(self.filter_set.rules),
            "is_default": self.filter_set.is_default
        } 
from typing import List, Dict, Any
from ..schemas.context import MessageContext, AuditResult

class ContentAuditor:
    def __init__(self, context: MessageContext):
        self.context = context
        self.safety_requirements = context.safety_requirements
        self.alignment_rules = context.alignment_rules

    def audit_response(self, response: str) -> AuditResult:
        """
        Audit a response against safety requirements and alignment rules.
        
        Args:
            response: The response text to audit
            
        Returns:
            AuditResult containing compliance status and any violations
        """
        violations = []
        
        # Check against safety requirements
        for requirement in self.safety_requirements:
            if not self._check_requirement(response, requirement):
                violations.append(f"Violates safety requirement: {requirement}")
        
        # Check against alignment rules
        for rule in self.alignment_rules:
            if not self._check_rule(response, rule):
                violations.append(f"Violates alignment rule: {rule}")
        
        # Determine severity based on number of violations
        severity = "high" if len(violations) > 2 else "medium" if len(violations) > 0 else "low"
        
        return AuditResult(
            compliant=len(violations) == 0,
            violations=violations,
            severity=severity,
            details={
                "context": {
                    "domain": self.context.domain,
                    "user_role": self.context.user_role
                },
                "rule_count": len(self.safety_requirements) + len(self.alignment_rules)
            }
        )

    def _check_requirement(self, response: str, requirement: str) -> bool:
        """
        Check if response meets a safety requirement.
        This is a simple implementation - in production, you'd want more sophisticated checks.
        """
        # Convert requirement to lowercase for case-insensitive matching
        requirement_lower = requirement.lower()
        response_lower = response.lower()
        
        # Example checks (customize based on your requirements)
        if "no medical advice" in requirement_lower:
            medical_terms = ["prescribe", "diagnose", "treatment", "medicine", "drug"]
            return not any(term in response_lower for term in medical_terms)
        
        if "be professional" in requirement_lower:
            unprofessional_terms = ["damn", "hell", "crap", "stupid"]
            return not any(term in response_lower for term in unprofessional_terms)
        
        # Default to True if no specific checks are implemented
        return True

    def _check_rule(self, response: str, rule: str) -> bool:
        """
        Check if response follows an alignment rule.
        This is a simple implementation - in production, you'd want more sophisticated checks.
        """
        # Convert rule to lowercase for case-insensitive matching
        rule_lower = rule.lower()
        response_lower = response.lower()
        
        # Example checks (customize based on your rules)
        if "use inclusive language" in rule_lower:
            exclusive_terms = ["he/she", "him/her", "guys", "mankind"]
            return not any(term in response_lower for term in exclusive_terms)
        
        if "avoid bias" in rule_lower:
            biased_terms = ["always", "never", "everyone", "nobody"]
            return not any(term in response_lower for term in biased_terms)
        
        # Default to True if no specific checks are implemented
        return True 
from typing import Optional
from ..schemas.context import MessageContext, SystemPrompt

DEFAULT_SYSTEM_PROMPT = """You are a helpful AI assistant. You aim to be truthful, harmless, and helpful."""

class PromptBuilder:
    def __init__(self, base_prompt: str = DEFAULT_SYSTEM_PROMPT):
        self.base_prompt = base_prompt

    def build_system_prompt(self, context: Optional[MessageContext] = None) -> str:
        """
        Build a system prompt incorporating MCP context.
        """
        if not context:
            return self.base_prompt

        prompt_parts = [self.base_prompt]

        # Add domain-specific context
        if context.domain:
            prompt_parts.append(f"\nDomain: {context.domain}")

        # Add user role context
        if context.user_role:
            prompt_parts.append(f"\nUser Role: {context.user_role}")

        # Add goals
        if context.goals:
            prompt_parts.append("\nGoals:")
            for goal in context.goals:
                prompt_parts.append(f"- {goal}")

        # Add safety requirements
        if context.safety_requirements:
            prompt_parts.append("\nSafety Requirements:")
            for req in context.safety_requirements:
                prompt_parts.append(f"- {req}")

        # Add alignment rules
        if context.alignment_rules:
            prompt_parts.append("\nAlignment Rules:")
            for rule in context.alignment_rules:
                prompt_parts.append(f"- {rule}")

        return "\n".join(prompt_parts)

    def update_base_prompt(self, new_prompt: str):
        """Update the base system prompt"""
        self.base_prompt = new_prompt 
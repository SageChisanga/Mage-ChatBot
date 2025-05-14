from pydantic import BaseModel
from typing import Optional, List, Dict, Any

class MessageContext(BaseModel):
    domain: str
    user_role: str
    safety_requirements: List[str]
    alignment_rules: List[str]
    additional_context: Optional[Dict[str, Any]] = None

class FilterSet(BaseModel):
    name: str
    description: Optional[str] = None
    rules: List[str]
    is_default: bool = False

class AuditResult(BaseModel):
    compliant: bool
    violations: List[str]
    severity: str
    details: Dict[str, Any]

class SystemPrompt(BaseModel):
    base_prompt: str
    context: Optional[MessageContext] = None
    filters: Optional[FilterSet] = None 
from pydantic import BaseModel
from typing import List, Optional
from .context import AuditResult

class ChatMessage(BaseModel):
    content: str
    domain: Optional[str] = None
    goals: Optional[List[str]] = None
    safety_requirements: Optional[List[str]] = None
    alignment_rules: Optional[List[str]] = None

class ChatResponse(BaseModel):
    message: str
    audit_result: Optional[AuditResult] = None 
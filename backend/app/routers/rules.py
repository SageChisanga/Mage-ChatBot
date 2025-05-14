from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional, Dict, Any
from backend.app.schemas.context import FilterSet, MessageContext, AuditResult
from backend.app.utils.filters import PromptFilter
from backend.app.utils.alignment import ContentAuditor
from backend.app.dependencies import get_current_user
from pydantic import BaseModel

rules_router = APIRouter(
    prefix="/rules",
    tags=["Rules"],
    responses={404: {"description": "Not found"}}
)

# Initialize global instances
prompt_filter = PromptFilter()

class RuleSet(BaseModel):
    name: str
    description: Optional[str] = None
    rules: List[str]
    is_default: bool = False

    class Config:
        schema_extra = {
            "example": {
                "name": "custom_filters",
                "description": "Custom filter rules for content moderation",
                "rules": ["(?i)inappropriate", "(?i)harmful"],
                "is_default": False
            }
        }

class AlignmentRuleSet(BaseModel):
    name: str
    description: Optional[str] = None
    safety_requirements: List[str]
    alignment_rules: List[str]
    is_default: bool = False

    class Config:
        schema_extra = {
            "example": {
                "name": "medical_alignment",
                "description": "Rules for medical domain",
                "safety_requirements": ["no medical advice", "be professional"],
                "alignment_rules": ["use inclusive language", "avoid bias"],
                "is_default": False
            }
        }

class RuleResponse(BaseModel):
    message: str
    summary: Dict[str, Any]

@rules_router.post("/filters", response_model=RuleResponse, status_code=status.HTTP_201_CREATED)
async def create_filter_rules(
    rule_set: RuleSet,
    current_user: dict = Depends(get_current_user)
):
    """
    Create or update custom filter rules.
    
    - **name**: Name of the filter set
    - **description**: Optional description of the filter set
    - **rules**: List of regex patterns for filtering
    - **is_default**: Whether this is the default filter set
    """
    try:
        filter_set = FilterSet(
            name=rule_set.name,
            description=rule_set.description,
            rules=rule_set.rules,
            is_default=rule_set.is_default
        )
        prompt_filter.update_filters(filter_set)
        return {
            "message": "Filter rules updated successfully",
            "summary": prompt_filter.get_filter_summary()
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@rules_router.get("/filters", response_model=Dict[str, Any])
async def get_filter_rules(current_user: dict = Depends(get_current_user)):
    """
    Get current filter rules.
    
    Returns a summary of the currently active filter rules.
    """
    return prompt_filter.get_filter_summary()

@rules_router.post("/alignment", response_model=Dict[str, Any], status_code=status.HTTP_201_CREATED)
async def create_alignment_rules(
    rule_set: AlignmentRuleSet,
    current_user: dict = Depends(get_current_user)
):
    """
    Create or update alignment rules.
    
    - **name**: Name of the alignment rule set
    - **description**: Optional description of the rule set
    - **safety_requirements**: List of safety requirements
    - **alignment_rules**: List of alignment rules
    - **is_default**: Whether this is the default rule set
    """
    try:
        test_context = MessageContext(
            user_id=current_user["id"],
            safety_requirements=rule_set.safety_requirements,
            alignment_rules=rule_set.alignment_rules
        )
        
        auditor = ContentAuditor(test_context)
        test_result = auditor.audit_response("Test response")
        
        return {
            "message": "Alignment rules updated successfully",
            "rule_set": rule_set.dict(),
            "test_result": test_result.dict()
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@rules_router.get("/alignment", response_model=Dict[str, List[str]])
async def get_alignment_rules(current_user: dict = Depends(get_current_user)):
    """
    Get current alignment rules.
    
    Returns the current safety requirements and alignment rules.
    """
    return {
        "safety_requirements": current_user.get("safety_requirements", []),
        "alignment_rules": current_user.get("alignment_rules", [])
    }

@rules_router.post("/test", response_model=Dict[str, Any])
async def test_rules(
    message: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Test a message against current rules.
    
    - **message**: The message to test against current rules
    
    Returns results from both prompt filtering and alignment checks.
    """
    is_safe, filter_violations = prompt_filter.check_prompt(message)
    
    context = MessageContext(
        user_id=current_user["id"],
        safety_requirements=current_user.get("safety_requirements", []),
        alignment_rules=current_user.get("alignment_rules", [])
    )
    auditor = ContentAuditor(context)
    alignment_result = auditor.audit_response(message)
    
    return {
        "prompt_filtering": {
            "is_safe": is_safe,
            "violations": filter_violations
        },
        "alignment_check": alignment_result.dict()
    } 
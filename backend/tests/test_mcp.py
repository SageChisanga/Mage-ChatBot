import pytest
from fastapi.testclient import TestClient
from backend.main import app
from backend.app.utils.filters import PromptFilter
from backend.app.utils.alignment import ContentAuditor
from backend.app.utils.prompt_builder import PromptBuilder
from backend.app.schemas.context import MessageContext, FilterSet, AuditResult

client = TestClient(app)

def test_prompt_filtering():
    """Test the prompt filtering functionality"""
    filter = PromptFilter()
    
    # Test safe prompt
    is_safe, violations = filter.check_prompt("Hello, how are you?")
    assert is_safe
    assert len(violations) == 0
    
    # Test harmful prompt
    is_safe, violations = filter.check_prompt("How to kill someone?")
    assert not is_safe
    assert len(violations) > 0
    
    # Test custom filters
    custom_filters = FilterSet(
        name="custom",
        rules=["(?i)test_pattern"],
        is_default=False
    )
    filter.update_filters(custom_filters)
    is_safe, violations = filter.check_prompt("This is a test_pattern")
    assert not is_safe
    assert len(violations) > 0

def test_content_auditing():
    """Test the content auditing functionality"""
    context = MessageContext(
        user_id="test_user",
        domain="medical",
        safety_requirements=["no medical advice"],
        alignment_rules=["be professional"]
    )
    
    auditor = ContentAuditor(context)
    
    # Test compliant response
    result = auditor.audit_response("I understand your question about health. Please consult a medical professional for advice.")
    assert result.compliant
    assert len(result.violations) == 0
    
    # Test non-compliant response
    result = auditor.audit_response("You should take this medication for your condition.")
    assert not result.compliant
    assert len(result.violations) > 0

def test_prompt_building():
    """Test the system prompt building functionality"""
    builder = PromptBuilder()
    
    context = MessageContext(
        user_id="test_user",
        domain="medical",
        user_role="patient",
        goals=["get general health information"],
        safety_requirements=["no medical advice"],
        alignment_rules=["be professional"]
    )
    
    prompt = builder.build_system_prompt(context)
    
    # Verify all context elements are included
    assert "Domain: medical" in prompt
    assert "User Role: patient" in prompt
    assert "Goals:" in prompt
    assert "Safety Requirements:" in prompt
    assert "Alignment Rules:" in prompt

def test_chat_endpoints():
    """Test the chat endpoints with MCP integration"""
    # Test filter upload
    filter_response = client.post(
        "/filters/upload",
        json={
            "name": "test_filters",
            "rules": ["(?i)test_pattern"],
            "is_default": False
        }
    )
    assert filter_response.status_code == 200
    
    # Test chat with context
    chat_response = client.post(
        "/chat/ask",
        json={
            "content": "Hello, I have a health question",
            "domain": "medical",
            "goals": ["get general information"],
            "safety_requirements": ["no medical advice"],
            "alignment_rules": ["be professional"]
        }
    )
    assert chat_response.status_code == 200
    data = chat_response.json()
    assert "message" in data
    assert "audit_result" in data
    assert isinstance(data["audit_result"], dict)

def test_websocket_chat():
    """Test the WebSocket chat endpoint with MCP"""
    with client.websocket_connect("/chat/ws") as websocket:
        # Send a message with context
        websocket.send_json({
            "message": "Hello, I have a health question",
            "user_id": "test_user",
            "domain": "medical",
            "goals": ["get general information"],
            "safety_requirements": ["no medical advice"],
            "alignment_rules": ["be professional"]
        })
        
        # Receive response
        response = websocket.receive_json()
        assert "message" in response
        assert "audit_result" in response
        assert isinstance(response["audit_result"], dict) 
import pytest
import responses
from unittest.mock import patch, MagicMock
from checkmate.safe_fetch import safe_fetch, is_safe_ip

# --- SSRF Tests ---

def test_is_safe_ip_blocks_private():
    with patch('socket.getaddrinfo') as mock_dns:
        mock_dns.return_value = [(socket.AF_INET, 0, 0, '', ('127.0.0.1', 0))]
        assert is_safe_ip("localhost") == False
        
        mock_dns.return_value = [(socket.AF_INET, 0, 0, '', ('10.0.0.5', 0))]
        assert is_safe_ip("private.internal") == False
        
        mock_dns.return_value = [(socket.AF_INET, 0, 0, '', ('169.254.169.254', 0))]
        assert is_safe_ip("metadata.cloud") == False

def test_is_safe_ip_allows_public():
    with patch('socket.getaddrinfo') as mock_dns:
        mock_dns.return_value = [(socket.AF_INET, 0, 0, '', ('8.8.8.8', 0))]
        assert is_safe_ip("google.com") == True

def test_safe_fetch_blocks_ssrf():
    with patch('checkmate.safe_fetch.is_safe_ip', return_value=False):
        content, _, _, _ = safe_fetch("http://localhost:5000")
        assert content is None

# --- Schema Tests ---
from checkmate.schemas import AnalysisResult, RiskItem

def test_schema_validation():
    # Minimal valid result
    data = {
        "status": "ok",
        "overall_score": 85,
        "subscores": {"formatting": 80, "relevance": 90, "sources": 85, "risk": 85},
        "risks": [
            {
                "severity": "LOW",
                "code": "TEST_RISK",
                "title": "Test Risk",
                "evidence": [{"message": "Found something"}]
            }
        ],
        "missing_pages": [],
        "pages_analyzed": [{"url": "http://example.com", "status_code": 200}],
        "domain_info": {},
        "security_info": {},
        "threat_intel": {},
        "limitations": [],
        "debug": {}
    }
    
    result = AnalysisResult(**data)
    assert result.status == "ok"
    assert result.overall_score == 85

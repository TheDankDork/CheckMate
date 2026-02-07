import pytest
import responses
import socket
from unittest.mock import patch, MagicMock
from checkmate.safe_fetch import safe_fetch, is_safe_ip
from checkmate.crawl import crawl_site

# --- SSRF Tests ---

def test_is_safe_ip_blocks_private():
    # Mock socket.getaddrinfo to return private IP
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
        artifact = safe_fetch("http://localhost:5000")
        assert "Blocked by SSRF protection" in artifact.errors

# --- Timeout Tests ---

@responses.activate
def test_safe_fetch_timeout():
    # Mock a timeout
    responses.add(responses.GET, "http://example.com", body=Exception("Timeout"))
    
    # We need to ensure is_safe_ip passes
    with patch('checkmate.safe_fetch.is_safe_ip', return_value=True):
        # We also need to patch requests.Session.get to raise Timeout since responses doesn't easily simulate read timeout with just body=Exception
        # Actually responses can raise exceptions
        with patch('requests.Session.get', side_effect=import_requests_timeout):
            artifact = safe_fetch("http://example.com")
            assert "Request timed out" in artifact.errors

def import_requests_timeout(*args, **kwargs):
    import requests
    raise requests.exceptions.Timeout()

# --- Crawl Tests ---

@responses.activate
def test_crawl_max_pages():
    start_url = "http://example.com"
    
    # Mock homepage with many links
    html_home = '<html><body>' + ''.join([f'<a href="/page{i}">Page {i}</a>' for i in range(20)]) + '</body></html>'
    responses.add(responses.GET, start_url, body=html_home, content_type='text/html')
    
    # Mock subpages
    for i in range(20):
        responses.add(responses.GET, f"http://example.com/page{i}", body="<html></html>", content_type='text/html')
    
    with patch('checkmate.safe_fetch.is_safe_ip', return_value=True):
        result = crawl_site(start_url)
        
        # Should be capped at MAX_PAGES (10)
        assert len(result.all_pages) <= 10
        assert result.stats["pages_crawled"] <= 10

@responses.activate
def test_crawl_finds_key_pages():
    start_url = "http://example.com"
    html_home = '<html><body><a href="/contact">Contact Us</a><a href="/privacy-policy">Privacy</a></body></html>'
    
    responses.add(responses.GET, start_url, body=html_home, content_type='text/html')
    responses.add(responses.GET, "http://example.com/contact", body="Contact Page", content_type='text/html')
    responses.add(responses.GET, "http://example.com/privacy-policy", body="Privacy Page", content_type='text/html')
    
    with patch('checkmate.safe_fetch.is_safe_ip', return_value=True):
        result = crawl_site(start_url)
        
        assert "contact" in result.key_pages
        assert "privacy" in result.key_pages

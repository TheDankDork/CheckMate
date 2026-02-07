import pytest
from checkmate.modules.extraction import extract_page_features, truncate_clean_text

HTML_LEGIT = """
<html>
<head><title>Legit Corp</title></head>
<body>
    <nav>Menu</nav>
    <h1>Welcome to Legit Corp</h1>
    <p>Contact us at support@legit.com or call +1-650-253-0000.</p>
    <p>We value your privacy.</p>
    <a href="/about">About Us</a>
    <a href="https://google.com">Search</a>
    <footer>Copyright 2023</footer>
</body>
</html>
"""

HTML_EMPTY = "<html><body></body></html>"

HTML_SCAM = """
<html>
<head><title>FREE MONEY</title></head>
<body>
    <h1>ACT NOW!!!</h1>
    <p>Enter your SSN and Credit Card Number to win $1,000,000.</p>
    <p>Limited time offer!</p>
</body>
</html>
"""

def test_extract_legit():
    features = extract_page_features(HTML_LEGIT, "https://legit.com")
    assert features["title"] == "Legit Corp"
    assert "Welcome to Legit Corp" in features["headings"]
    assert "support@legit.com" in features["emails"]
    assert "+16502530000" in features["phones"]
    assert "https://legit.com/about" in features["links_internal"]
    assert "https://google.com" in features["links_external"]
    assert "Menu" not in features["clean_text"] # nav removed

def test_extract_empty():
    features = extract_page_features(HTML_EMPTY, "https://example.com")
    assert features["title"] is None
    assert features["clean_text"] == ""

def test_extract_scam_keywords():
    features = extract_page_features(HTML_SCAM, "https://scam.com")
    assert features["keyword_hits"]["asks_ssn"] == True
    assert features["keyword_hits"]["asks_credit_card"] == True
    assert features["keyword_hits"]["payment_pressure_terms"] == True

def test_truncate():
    long_text = "a" * 15000
    truncated = truncate_clean_text(long_text, max_chars=12000)
    assert len(truncated) == 12000

import logging
from urllib.parse import urlparse, urljoin
from bs4 import BeautifulSoup
from .models import ExtractionResult, PageArtifact
from .safe_fetch import safe_fetch

MAX_PAGES = 10
MAX_DEPTH = 2
KEY_PAGE_KEYWORDS = ["contact", "about", "privacy", "terms", "conditions"]

def is_internal_link(base_url: str, target_url: str) -> bool:
    base_domain = urlparse(base_url).netloc
    target_domain = urlparse(target_url).netloc
    return base_domain == target_domain or not target_domain

def get_links(html: str, base_url: str) -> list[str]:
    if not html:
        return []
    soup = BeautifulSoup(html, 'html.parser')
    links = []
    for a in soup.find_all('a', href=True):
        href = a['href']
        full_url = urljoin(base_url, href)
        links.append(full_url)
    return links

def crawl_site(start_url: str) -> ExtractionResult:
    result = ExtractionResult()
    
    queue = [(start_url, 0)]
    visited = set()
    pages_fetched = 0
    
    # First fetch the homepage
    # We treat the start_url as depth 0
    
    while queue and pages_fetched < MAX_PAGES:
        url, depth = queue.pop(0)
        
        if url in visited:
            continue
        visited.add(url)
        
        if depth > MAX_DEPTH:
            continue

        # Fetch the page
        artifact = safe_fetch(url)
        pages_fetched += 1
        
        # Store in all_pages
        result.all_pages.append(artifact)
        
        # If it's the primary page (first one)
        if pages_fetched == 1:
            result.primary_page = artifact

        # Check for errors before parsing
        if artifact.errors or not artifact.html:
            continue

        # Parse links for crawling
        links = get_links(artifact.html, artifact.final_url or url)
        
        # Populate artifact links (simple extraction for now)
        # Real extraction module might do better job later
        for link in links:
            if is_internal_link(url, link):
                artifact.links_internal.append(link)
                # Add to queue if internal and within depth
                if depth + 1 <= MAX_DEPTH:
                    queue.append((link, depth + 1))
            else:
                artifact.links_external.append(link)

        # Check if it's a key page
        url_lower = url.lower()
        for kw in KEY_PAGE_KEYWORDS:
            if kw in url_lower:
                # Simple heuristic: if keyword in URL, map it
                # We might want to be more specific, e.g. mapping "privacy-policy" to "privacy"
                # For now, just add to the dict with the keyword as key
                # If multiple keywords match, it might get overwritten or we pick first
                # The requirement says: key_pages{contact/about/privacy/terms}
                
                # normalize key
                key_name = kw
                if kw == "conditions": key_name = "terms"
                
                if key_name not in result.key_pages:
                     result.key_pages[key_name] = artifact
                break

    result.stats["pages_crawled"] = pages_fetched
    return result

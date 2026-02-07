import socket
import ipaddress
import requests
from urllib.parse import urlparse
from typing import Optional, Tuple

# Blocked ranges
BLOCKED_NETWORKS = [
    ipaddress.ip_network("127.0.0.0/8"),
    ipaddress.ip_network("10.0.0.0/8"),
    ipaddress.ip_network("172.16.0.0/12"),
    ipaddress.ip_network("192.168.0.0/16"),
    ipaddress.ip_network("169.254.0.0/16"),
    ipaddress.ip_network("224.0.0.0/4"),
    ipaddress.ip_network("240.0.0.0/4"),
]

def is_safe_ip(hostname: str) -> bool:
    try:
        ip_list = socket.getaddrinfo(hostname, None)
        for family, _, _, _, sockaddr in ip_list:
            ip_str = sockaddr[0]
            try:
                ip_obj = ipaddress.ip_address(ip_str)
            except ValueError:
                continue 

            if ip_obj.is_loopback or ip_obj.is_private or ip_obj.is_multicast or ip_obj.is_reserved:
                return False
            
            for net in BLOCKED_NETWORKS:
                if ip_obj in net:
                    return False
                    
            if str(ip_obj) == "169.254.169.254":
                return False
                
        return True
    except socket.gaierror:
        return False 

def safe_fetch(url: str, timeout: int = 10) -> Tuple[Optional[str], Optional[int], Optional[str], Optional[str]]:
    """
    Fetches a URL safely with SSRF protection.
    Returns: (content, status_code, content_type, final_url) or (None, None, None, None) on error
    """
    parsed = urlparse(url)
    if parsed.scheme not in ('http', 'https'):
        return None, None, None, None

    if not parsed.hostname or not is_safe_ip(parsed.hostname):
        return None, None, None, None

    session = requests.Session()
    session.max_redirects = 3
    
    current_url = url
    
    try:
        for _ in range(4): 
            parsed_curr = urlparse(current_url)
            if not is_safe_ip(parsed_curr.hostname):
                return None, None, None, None

            response = session.get(
                current_url, 
                timeout=timeout, 
                verify=True, 
                allow_redirects=False, 
                stream=True 
            )
            
            if response.is_redirect:
                location = response.headers.get('Location')
                if not location:
                    break
                
                if location.startswith('/'):
                    current_url = f"{parsed_curr.scheme}://{parsed_curr.netloc}{location}"
                elif location.startswith('http'):
                    current_url = location
                else:
                    current_url = location
                continue
            else:
                content = b""
                for chunk in response.iter_content(chunk_size=8192):
                    content += chunk
                    if len(content) > 2 * 1024 * 1024: # 2MB limit
                        return None, None, None, None
                
                text_content = None
                content_type = response.headers.get('Content-Type', '')
                
                if 'text/html' in content_type or 'text/plain' in content_type:
                    text_content = content.decode('utf-8', errors='replace')
                
                return text_content, response.status_code, content_type, response.url
        
        return None, None, None, None

    except Exception:
        return None, None, None, None

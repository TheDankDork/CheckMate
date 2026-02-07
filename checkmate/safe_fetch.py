import socket
import ipaddress
import requests
from urllib.parse import urlparse
from datetime import datetime
from .models import PageArtifact

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
        # Resolve hostname to IP
        # Note: This only checks the first IP returned. 
        # For robust production SSRF, you'd need to check all IPs or hook into the socket connection.
        ip_list = socket.getaddrinfo(hostname, None)
        for family, _, _, _, sockaddr in ip_list:
            ip_str = sockaddr[0]
            try:
                ip_obj = ipaddress.ip_address(ip_str)
            except ValueError:
                continue # Skip invalid IPs (e.g. IPv6 scope ids if not handled)

            if ip_obj.is_loopback or ip_obj.is_private or ip_obj.is_multicast or ip_obj.is_reserved:
                return False
            
            # Check explicit blocked networks
            for net in BLOCKED_NETWORKS:
                if ip_obj in net:
                    return False
                    
            # Explicit check for cloud metadata
            if str(ip_obj) == "169.254.169.254":
                return False
                
        return True
    except socket.gaierror:
        return False # DNS resolution failed

def safe_fetch(url: str) -> PageArtifact:
    artifact = PageArtifact(url=url)
    
    parsed = urlparse(url)
    if parsed.scheme not in ('http', 'https'):
        artifact.errors.append(f"Unsupported scheme: {parsed.scheme}")
        return artifact

    if not parsed.hostname:
        artifact.errors.append("Invalid URL: no hostname")
        return artifact

    # Initial SSRF check
    if not is_safe_ip(parsed.hostname):
        artifact.errors.append("Blocked by SSRF protection")
        return artifact

    session = requests.Session()
    session.max_redirects = 3
    
    # We need to manually handle redirects to check SSRF at each step
    # or trust that the initial check + standard library behavior is enough for MVP.
    # The prompt says: "Limit redirects (e.g., max 3) and re-check SSRF rules after each redirect."
    
    current_url = url
    history = []
    
    try:
        # Manual redirect loop to enforce SSRF on each hop
        for _ in range(4): # 0 to 3 redirects
            # Check IP of current target
            parsed_curr = urlparse(current_url)
            if not is_safe_ip(parsed_curr.hostname):
                artifact.errors.append(f"Redirect blocked by SSRF: {current_url}")
                return artifact

            response = session.get(
                current_url, 
                timeout=10, 
                verify=True, 
                allow_redirects=False, 
                stream=True # Stream to check size
            )
            
            if response.is_redirect:
                location = response.headers.get('Location')
                if not location:
                    break
                
                # Handle relative redirects
                if location.startswith('/'):
                    current_url = f"{parsed_curr.scheme}://{parsed_curr.netloc}{location}"
                elif location.startswith('http'):
                    current_url = location
                else:
                    # simplistic handling for other cases
                    current_url = location
                
                history.append(response)
                continue
            else:
                # Final response
                # Check size limit (2MB)
                content = b""
                for chunk in response.iter_content(chunk_size=8192):
                    content += chunk
                    if len(content) > 2 * 1024 * 1024:
                        artifact.errors.append("Response too large (>2MB)")
                        return artifact
                
                artifact.final_url = response.url
                artifact.status_code = response.status_code
                artifact.content_type = response.headers.get('Content-Type', '')
                
                # Only save text/html content
                if 'text/html' in artifact.content_type or 'text/plain' in artifact.content_type:
                    artifact.html = content.decode('utf-8', errors='replace')
                    artifact.text = artifact.html # Placeholder, extraction module will clean this
                
                return artifact
        
        artifact.errors.append("Too many redirects")
        return artifact

    except requests.exceptions.Timeout:
        artifact.errors.append("Request timed out")
    except requests.exceptions.SSLError:
        artifact.errors.append("SSL verification failed")
    except requests.exceptions.RequestException as e:
        artifact.errors.append(f"Request failed: {str(e)}")
    except Exception as e:
        artifact.errors.append(f"Unexpected error: {str(e)}")

    return artifact

"""Validators for inputs."""
import re
from urllib.parse import urlparse
from typing import Tuple


def validate_url(url: str) -> Tuple[bool, str]:
    """
    Validate URL format.
    
    Args:
        url: URL string to validate
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not url:
        return False, "URL cannot be empty"
    
    # Basic URL regex
    url_pattern = r'^https?://(?:www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b(?:[-a-zA-Z0-9()@:%_\+.~#?&/=]*)$'
    
    if not re.match(url_pattern, url):
        return False, "Invalid URL format"
    
    try:
        result = urlparse(url)
        if not all([result.scheme, result.netloc]):
            return False, "URL must have scheme (http/https) and domain"
    except Exception as e:
        return False, f"URL parsing error: {str(e)}"
    
    return True, ""


def validate_business_name(name: str) -> Tuple[bool, str]:
    """Validate business name."""
    if not name or not isinstance(name, str):
        return False, "Business name must be a non-empty string"
    
    if len(name) < 2:
        return False, "Business name must be at least 2 characters"
    
    if len(name) > 200:
        return False, "Business name must be less than 200 characters"
    
    return True, ""

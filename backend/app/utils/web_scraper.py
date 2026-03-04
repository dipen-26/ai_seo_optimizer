"""Web scraper utility for fetching and parsing HTML."""
import httpx
from bs4 import BeautifulSoup
from typing import Optional, Dict, Any
import asyncio
from ..core.config import HTTP_TIMEOUT, SCRAPE_TIMEOUT


async def fetch_html(url: str) -> Optional[str]:
    """
    Fetch HTML content from a URL using httpx.
    
    Args:
        url: URL to fetch
        
    Returns:
        HTML content or None if fetch fails
    """
    try:
        async with httpx.AsyncClient(timeout=HTTP_TIMEOUT) as client:
            response = await client.get(
                url,
                follow_redirects=True,
                headers={
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
                }
            )
            response.raise_for_status()
            return response.text
    except asyncio.TimeoutError:
        return None
    except httpx.RequestError:
        return None
    except Exception:
        return None


def parse_html(html: str) -> Optional[BeautifulSoup]:
    """
    Parse HTML content using BeautifulSoup.
    
    Args:
        html: HTML string
        
    Returns:
        BeautifulSoup object or None
    """
    try:
        return BeautifulSoup(html, "html.parser")
    except Exception:
        return None


async def scrape_page(url: str) -> Optional[Dict[str, Any]]:
    """
    Scrape a complete page and return parsed content.
    
    Args:
        url: URL to scrape
        
    Returns:
        Dictionary with page data or None
    """
    html = await fetch_html(url)
    if not html:
        return None
    
    soup = parse_html(html)
    if not soup:
        return None
    
    return {
        "html": html,
        "soup": soup
    }

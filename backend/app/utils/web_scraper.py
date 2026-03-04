"""Web Scraper with Playwright integration for JavaScript rendering."""
from typing import Dict, Any, Optional
import httpx


class WebScraper:
    """Web scraper with async Playwright for JS rendering."""
    
    def __init__(self):
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate",
            "Connection": "keep-alive",
        }
    
    async def scrape(self, url: str) -> Dict[str, Any]:
        """Scrape a URL using async Playwright, fallback to httpx."""
        
        # Try async Playwright first
        playwright_result = await self._scrape_async_playwright(url)
        if playwright_result and playwright_result.get("html"):
            return playwright_result
        
        # Fallback to httpx if Playwright fails
        return await self._scrape_httpx(url)
    
    async def _scrape_async_playwright(self, url: str) -> Optional[Dict[str, Any]]:
        """Use async Playwright for scraping."""
        try:
            from playwright.async_api import async_playwright
            
            async with async_playwright() as p:
                browser = await p.chromium.launch(
                    headless=True,
                    args=['--no-sandbox', '--disable-setuid-sandbox']
                )
                page = await browser.new_page()
                await page.goto(url, wait_until="networkidle", timeout=30000)
                html = await page.content()
                await browser.close()
                
                return {
                    "html": html,
                    "method": "async_playwright",
                    "success": True
                }
        except Exception as e:
            print(f"Async Playwright failed: {e}")
            return None

    
    async def _scrape_httpx(self, url: str) -> Dict[str, Any]:
        """Fallback to httpx for static HTML."""
        try:
            async with httpx.AsyncClient(timeout=30, follow_redirects=True) as client:
                response = await client.get(url, headers=self.headers)
                
                return {
                    "html": response.text,
                    "method": "httpx",
                    "success": response.status_code == 200,
                    "status_code": response.status_code
                }
        except Exception as e:
            return {
                "html": "",
                "method": "httpx",
                "success": False,
                "error": str(e)
            }
    
    async def scrape_with_viewport(self, url: str) -> Dict[str, Any]:
        """Scrape and detect viewport visibility using async Playwright."""
        result = await self.scrape(url)
        
        if result.get("method") == "httpx":
            # Can't detect viewport with httpx
            result["viewport_analysis"] = {"available": False}
            return result
        
        try:
            from playwright.async_api import async_playwright
            
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True)
                page = await browser.new_page(viewport={"width": 1280, "height": 720})
                await page.goto(url, wait_until="networkidle", timeout=30000)
                
                # Get page title
                title = await page.title()
                
                # Check for common CTA selectors
                cta_selectors = [
                    "button", "a.btn", "[role='button']", 
                    "input[type='submit']", ".cta", ".call-to-action"
                ]
                
                ctas_above_fold = []
                ctas_below_fold = []
                
                for selector in cta_selectors:
                    try:
                        elements = await page.query_selector_all(selector)
                        for el in elements:
                            box = await el.bounding_box()
                            if box:
                                if box["y"] < 720:
                                    ctas_above_fold.append(selector)
                                else:
                                    ctas_below_fold.append(selector)
                    except:
                        pass
                
                await browser.close()
                
                result["viewport_analysis"] = {
                    "available": True,
                    "title": title,
                    "ctas_above_fold": len(ctas_above_fold),
                    "ctas_below_fold": len(ctas_below_fold),
                    "viewport_height": 720
                }
                
        except Exception as e:
            result["viewport_analysis"] = {"available": False, "error": str(e)}
        
        return result


# Module-level functions for compatibility
_scraper = WebScraper()


async def scrape_page(url: str) -> Dict[str, Any]:
    """Scrape a page and return HTML content."""
    return await _scraper.scrape(url)


async def get_pagespeed_data(url: str) -> Dict[str, Any]:
    """Get Google PageSpeed Insights data."""
    from ..core.config import PAGESPEED_API_KEY
    
    if not PAGESPEED_API_KEY:
        return {
            "available": False,
            "message": "PageSpeed API key not configured"
        }
    
    try:
        async with httpx.AsyncClient(timeout=30) as client:
            params = {
                "url": url,
                "strategy": "mobile",
                "key": PAGESPEED_API_KEY
            }
            response = await client.get(
                "https://www.googleapis.com/pagespeedonline/v5/runPagespeed",
                params=params
            )
            
            if response.status_code == 200:
                data = response.json()
                lighthouse = data.get("lighthouseResult", {})
                audits = lighthouse.get("audits", {})
                
                return {
                    "available": True,
                    "score": lighthouse.get("categories", {}).get("performance", {}).get("score", 0) * 100,
                    "lcp": audits.get("largest-contentful-paint", {}).get("displayValue", "N/A"),
                    "fid": audits.get("max-potential-fid", {}).get("displayValue", "N/A"),
                    "cls": audits.get("cumulative-layout-shift", {}).get("displayValue", "N/A"),
                    "tti": audits.get("interactive", {}).get("displayValue", "N/A"),
                    "fcp": audits.get("first-contentful-paint", {}).get("displayValue", "N/A"),
                    "si": audits.get("speed-index", {}).get("displayValue", "N/A")
                }
            else:
                return {
                    "available": False,
                    "message": f"PageSpeed API error: {response.status_code}"
                }
    except Exception as e:
        return {
            "available": False,
            "message": str(e)
        }

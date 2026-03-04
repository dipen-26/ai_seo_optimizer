"""Playwright utilities for viewport detection."""
from typing import Optional, Dict, Any, List
import asyncio


async def detect_above_fold_elements(url: str) -> Optional[Dict[str, Any]]:
    """
    Detect which CTA elements are above the fold using Playwright.
    
    Args:
        url: URL to analyze
        
    Returns:
        Dictionary with above-fold elements or None
    """
    try:
        from playwright.async_api import async_playwright
        from ..core.config import (
            PLAYWRIGHT_TIMEOUT,
            PLAYWRIGHT_VIEWPORT_WIDTH,
            PLAYWRIGHT_VIEWPORT_HEIGHT
        )
        
        async with async_playwright() as p:
            browser = await p.chromium.launch(
                headless=True,
                args=['--no-sandbox', '--disable-setuid-sandbox', '--disable-dev-shm-usage']
            )
            
            context = await browser.new_context(
                viewport={"width": PLAYWRIGHT_VIEWPORT_WIDTH, "height": PLAYWRIGHT_VIEWPORT_HEIGHT}
            )
            
            page = await context.new_page()
            page.set_default_timeout(PLAYWRIGHT_TIMEOUT)
            
            try:
                await page.goto(url, wait_until="networkidle", timeout=PLAYWRIGHT_TIMEOUT)
                await page.wait_for_timeout(1500)
                
                # Get viewport info
                viewport_info = await page.evaluate("""() => {
                    return {
                        width: window.innerWidth,
                        height: window.innerHeight
                    };
                }""")
                
                viewport_height = viewport_info.get("height", 720)
                viewport_width = viewport_info.get("width", 1280)
                
                # Find buttons above fold
                buttons_above_fold = []
                buttons_below_fold = []
                
                # Check <button> elements
                buttons = await page.query_selector_all("button")
                for btn in buttons:
                    box = await btn.bounding_box()
                    if box and box.get("y", 999) < viewport_height:
                        text = await btn.inner_text()
                        buttons_above_fold.append({"type": "button", "text": text[:50] if text else ""})
                    elif box:
                        text = await btn.inner_text()
                        buttons_below_fold.append({"type": "button", "text": text[:50] if text else ""})
                
                # Check <a> with button classes
                a_buttons = await page.query_selector_all("a.btn, a.button, a.cta, a[class*='btn'], a[class*='button'], a[class*='cta']")
                for btn in a_buttons:
                    box = await btn.bounding_box()
                    if box and box.get("y", 999) < viewport_height:
                        text = await btn.inner_text()
                        buttons_above_fold.append({"type": "link", "text": text[:50] if text else ""})
                    elif box:
                        text = await btn.inner_text()
                        buttons_below_fold.append({"type": "link", "text": text[:50] if text else ""})
                
                # Check input submit buttons
                inputs = await page.query_selector_all("input[type='submit'], input[type='button']")
                for inp in inputs:
                    box = await inp.bounding_box()
                    if box and box.get("y", 999) < viewport_height:
                        text = await inp.get_attribute("value") or "Submit"
                        buttons_above_fold.append({"type": "input_submit", "text": text[:50]})
                    elif box:
                        text = await inp.get_attribute("value") or "Submit"
                        buttons_below_fold.append({"type": "input_submit", "text": text[:50]})
                
                # Check elements with role="button"
                role_buttons = await page.query_selector_all("[role='button']")
                for btn in role_buttons:
                    box = await btn.bounding_box()
                    if box and box.get("y", 999) < viewport_height:
                        text = await btn.inner_text()
                        buttons_above_fold.append({"type": "role_button", "text": text[:50] if text else ""})
                    elif box:
                        text = await btn.inner_text()
                        buttons_below_fold.append({"type": "role_button", "text": text[:50] if text else ""})
                
                await browser.close()
                
                return {
                    "viewport": {
                        "width": viewport_width,
                        "height": viewport_height
                    },
                    "cta_above_fold": buttons_above_fold,
                    "cta_below_fold": buttons_below_fold,
                    "cta_above_fold_count": len(buttons_above_fold),
                    "cta_below_fold_count": len(buttons_below_fold),
                    "has_cta_above_fold": len(buttons_above_fold) > 0
                }
                
            except Exception:
                await browser.close()
                return None
                
    except ImportError:
        return None
    except Exception:
        return None


async def get_element_positions(url: str) -> Optional[List[Dict[str, Any]]]:
    """
    Get positions of key conversion elements.
    
    Args:
        url: URL to analyze
        
    Returns:
        List of element positions or None
    """
    try:
        from playwright.async_api import async_playwright
        from ..core.config import PLAYWRIGHT_TIMEOUT
        
        async with async_playwright() as p:
            browser = await p.chromium.launch(
                headless=True,
                args=['--no-sandbox', '--disable-setuid-sandbox']
            )
            
            page = await browser.new_page()
            page.set_default_timeout(PLAYWRIGHT_TIMEOUT)
            
            try:
                await page.goto(url, wait_until="networkidle", timeout=PLAYWRIGHT_TIMEOUT)
                await page.wait_for_timeout(1000)
                
                elements = []
                
                # Get all headings
                for level in range(1, 7):
                    tags = await page.query_selector_all(f"h{level}")
                    for tag in tags:
                        box = await tag.bounding_box()
                        if box:
                            text = await tag.inner_text()
                            elements.append({
                                "tag": f"h{level}",
                                "text": text[:100] if text else "",
                                "y": box.get("y", 0),
                                "x": box.get("x", 0),
                                "height": box.get("height", 0),
                                "width": box.get("width", 0)
                            })
                
                # Get forms
                forms = await page.query_selector_all("form")
                for form in forms:
                    box = await form.bounding_box()
                    if box:
                        action = await form.get_attribute("action") or ""
                        elements.append({
                            "tag": "form",
                            "action": action,
                            "y": box.get("y", 0),
                            "x": box.get("x", 0),
                            "height": box.get("height", 0),
                            "width": box.get("width", 0)
                        })
                
                await browser.close()
                return elements
                
            except Exception:
                await browser.close()
                return None
                
    except Exception:
        return None

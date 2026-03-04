"""CRO Service orchestrating audit flow with Playwright and PageSpeed integration."""
from typing import Dict, Any, Optional
from ..utils.validators import validate_url
from ..utils.web_scraper import scrape_page, get_pagespeed_data
from ..utils.viewport_detector import detect_above_fold_elements
from ..utils.data_extractor import CRODataExtractor
from .cro_scoring_service import CROScoringEngine
from .ai_service import AIService
from ..core.config import VALID_INDUSTRIES


class CROService:
    """
    Main CRO audit service.
    Orchestrates: validation → JS rendering scraping → extraction → scoring → AI recommendations.
    """
    
    def __init__(self):
        """Initialize CRO service."""
        self.ai_service = AIService()
    
    async def audit_url(
        self,
        url: str,
        goal: Optional[str] = None,
        notes: Optional[str] = None,
        industry: Optional[str] = "default"
    ) -> Dict[str, Any]:
        """
        Perform complete CRO audit on a URL.
        
        Args:
            url: URL to audit
            goal: Conversion goal
            notes: Additional context
            industry: Industry type for weighted scoring (saas, restaurant, ecommerce, healthcare, real_estate)
            
        Returns:
            Audit results including score, issues, and recommendations
        """
        
        # Validate industry
        if industry and industry.lower() not in VALID_INDUSTRIES:
            industry = "default"
        else:
            industry = industry.lower() if industry else "default"
        
        # Step 1: Validate URL
        is_valid, error = validate_url(url)
        if not is_valid:
            return {
                "success": False,
                "error": error,
                "score": 0,
                "issues": [],
                "recommendations": [],
                "ai_suggestions": []
            }
        
        # Step 2: Scrape page with Playwright (JavaScript rendering)
        page_data = await scrape_page(url)
        if not page_data or not page_data.get("html"):
            return {
                "success": False,
                "error": "Failed to fetch the URL. Check if the URL is accessible.",
                "score": 0,
                "issues": [],
                "recommendations": [],
                "ai_suggestions": []
            }
        
        # Parse HTML with BeautifulSoup
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(page_data["html"], "html.parser")
        page_data["soup"] = soup
        
        # Step 3: Extract data (with page_data for trust signals and viewport info)
        extractor = CRODataExtractor(soup, page_data)
        extracted_data = extractor.extract_all()
        
        # Step 4: Get PageSpeed data (async)
        pagespeed_data = None
        try:
            pagespeed_data = await get_pagespeed_data(url)
        except Exception:
            pass  # PageSpeed is optional
        
        # Step 5: Detect above-the-fold CTAs (async)
        viewport_data = None
        try:
            viewport_data = await detect_above_fold_elements(url)
            if viewport_data:
                # Add viewport data to extracted data
                extracted_data["cta_positions"]["above_fold"] = viewport_data.get("has_cta_above_fold", False)
                extracted_data["cta_positions"]["cta_above_fold_count"] = viewport_data.get("cta_above_fold_count", 0)
                extracted_data["cta_positions"]["cta_below_fold_count"] = viewport_data.get("cta_below_fold_count", 0)
                extracted_data["cta_positions"]["cta_above_fold"] = viewport_data.get("cta_above_fold", [])
        except Exception:
            pass  # Viewport detection is optional
        
        # Step 6: Score with industry-specific weights and PageSpeed data
        scorer = CROScoringEngine(extracted_data, industry, pagespeed_data)
        score, issues = scorer.calculate_score()
        
        # Step 7: Generate AI recommendations with enriched page context
        ai_suggestions = await self.ai_service.generate_cro_recommendations(
            score=score,
            extracted_data=extracted_data,
            issues=issues,
            goal=goal,
            industry=industry,
            pagespeed_data=pagespeed_data,
            viewport_data=viewport_data
        )
        
        # Generate basic recommendations
        recommendations = self._get_recommendations(score, issues)
        
        # Build response
        response = {
            "success": True,
            "score": score,
            "issues": issues,
            "recommendations": recommendations,
            "ai_suggestions": ai_suggestions or [],
            "extracted_data": {
                "title": extracted_data.get("title"),
                "meta_description": extracted_data.get("meta_description"),
                "h1_count": len(extracted_data.get("h1_tags", [])),
                "h1_text": extracted_data.get("h1_tags", []),
                "button_count": len(extracted_data.get("buttons", [])),
                "buttons": extracted_data.get("buttons", []),
                "form_count": len(extracted_data.get("forms", [])),
                "image_count": len(extracted_data.get("images", [])),
                "is_https": page_data.get("is_https", False),
                "js_rendered": page_data.get("js_rendered", False),
                "trust_signals": extracted_data.get("trust_signals", {}),
                "schema_types": extracted_data.get("schema", {}).get("schema_types", []),
                "cta_positions": extracted_data.get("cta_positions", {})
            },
            "industry": industry,
            "pagespeed": pagespeed_data
        }
        
        # Add viewport data if available
        if viewport_data:
            response["viewport_analysis"] = {
                "viewport": viewport_data.get("viewport", {}),
                "cta_above_fold": viewport_data.get("cta_above_fold_count", 0),
                "cta_below_fold": viewport_data.get("cta_below_fold_count", 0),
                "has_cta_above_fold": viewport_data.get("has_cta_above_fold", False)
            }
        
        return response
    
    def _get_recommendations(self, score: int, issues: list) -> list:
        """Generate non-AI recommendations based on issues."""
        recommendations = []
        
        # Add recommendations from critical issues
        for issue in issues:
            if issue.get("level") == "critical":
                recommendations.append(issue.get("detail", ""))
        
        # Add generic recommendations if score is low
        if score < 50:
            recommendations.append("Restructure page for better conversion focus")
            recommendations.append("Simplify the user journey to primary conversion goal")
        elif score < 75:
            recommendations.append("Refine existing copy for better clarity and urgency")
        
        return recommendations[:6]  # Limit to 6

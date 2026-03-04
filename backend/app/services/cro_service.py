"""CRO Service orchestrating audit flow."""
from typing import Dict, Any, Optional
from ..utils.validators import validate_url
from ..utils.web_scraper import scrape_page
from ..utils.data_extractor import CRODataExtractor
from .cro_scoring_service import CROScoringEngine
from .ai_service import AIService


class CROService:
    """
    Main CRO audit service.
    Orchestrates: validation → scraping → extraction → scoring → AI recommendations.
    """
    
    def __init__(self):
        """Initialize CRO service."""
        self.ai_service = AIService()
    
    async def audit_url(
        self,
        url: str,
        goal: Optional[str] = None,
        notes: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Perform complete CRO audit on a URL.
        
        Args:
            url: URL to audit
            goal: Conversion goal
            notes: Additional context
            
        Returns:
            Audit results including score, issues, and recommendations
        """
        
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
        
        # Step 2: Scrape page
        page_data = await scrape_page(url)
        if not page_data:
            return {
                "success": False,
                "error": "Failed to fetch the URL. Check if the URL is accessible.",
                "score": 0,
                "issues": [],
                "recommendations": [],
                "ai_suggestions": []
            }
        
        # Step 3: Extract data
        extractor = CRODataExtractor(page_data["soup"])
        extracted_data = extractor.extract_all()
        
        # Step 4: Score
        scorer = CROScoringEngine(extracted_data)
        score, issues = scorer.calculate_score()
        
        # Step 5: Generate recommendations
        ai_suggestions = await self.ai_service.generate_cro_recommendations(
            score=score,
            extracted_data=extracted_data,
            issues=issues,
            goal=goal
        )
        
        # Generate basic recommendations
        recommendations = self._get_recommendations(score, issues)
        
        return {
            "success": True,
            "score": score,
            "issues": issues,
            "recommendations": recommendations,
            "ai_suggestions": ai_suggestions or [],
            "extracted_data": {
                "title": extracted_data.get("title"),
                "meta_description": extracted_data.get("meta_description"),
                "h1_count": len(extracted_data.get("h1_tags", [])),
                "button_count": len(extracted_data.get("buttons", [])),
                "form_count": len(extracted_data.get("forms", [])),
                "image_count": len(extracted_data.get("images", []))
            }
        }
    
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

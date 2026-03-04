"""GMB Service orchestrating audit flow."""
from typing import Dict, Any, Optional, List
from ..utils.validators import validate_business_name
from ..utils.gmb_data_extractor import GMBDataExtractor
from ..services.gmb_scoring_service import GMBScoringEngine
from ..services.ai_service import AIService


class GMBService:
    """
    Main GMB audit service.
    Orchestrates: validation → data extraction → scoring → AI recommendations.
    """
    
    def __init__(self):
        """Initialize GMB service."""
        self.ai_service = AIService()
    
    async def audit_business(
        self,
        business_name: str,
        address: Optional[str] = None,
        category: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Perform complete GMB audit on a business.
        
        Args:
            business_name: Name of the business
            address: Optional business address/location
            category: Optional business category
            
        Returns:
            Audit results including score, issues, and recommendations
        """
        
        # Step 1: Validate business name
        is_valid, error = validate_business_name(business_name)
        if not is_valid:
            return {
                "success": False,
                "error": error,
                "score": 0,
                "issues": [],
                "recommendations": [],
                "ai_suggestions": [],
                "metrics": {}
            }
        
        # Step 2: Extract data (mock for now, real API integration in Phase 2)
        extractor = GMBDataExtractor(business_name, address)
        extracted_data = extractor.extract_all()
        
        # Step 3: Score
        scorer = GMBScoringEngine(extracted_data)
        score, issues, breakdown = scorer.calculate_score()
        
        # Step 4: Generate AI recommendations
        ai_suggestions = await self.ai_service.generate_gmb_recommendations(
            score=score,
            business_name=business_name,
            location=address or "Not specified",
            extracted_data=extracted_data,
            issues=issues
        )
        
        # Generate basic recommendations
        recommendations = self._get_recommendations(score, issues)
        
        return {
            "success": True,
            "score": score,
            "issues": issues,
            "recommendations": recommendations,
            "ai_suggestions": ai_suggestions or [],
            "metrics": {
                "profile_completeness": breakdown.get("profile_completeness", 0),
                "reviews": breakdown.get("reviews", 0),
                "photos": breakdown.get("photos", 0),
                "posts": breakdown.get("posts", 0),
                "engagement": breakdown.get("engagement", 0),
                "rating": extracted_data.get("review_data", {}).get("average_rating", 0),
                "review_count": extracted_data.get("review_data", {}).get("total_reviews", 0),
                "photo_count": extracted_data.get("content_metrics", {}).get("photo_count", 0),
                "post_count": extracted_data.get("content_metrics", {}).get("post_count", 0)
            },
            "extracted_data": {
                "business_name": extracted_data.get("business_name"),
                "location": extracted_data.get("location"),
                "categories": extracted_data.get("profile_data", {}).get("categories", []),
                "phone": extracted_data.get("profile_data", {}).get("phone", ""),
                "website": extracted_data.get("profile_data", {}).get("website", "")
            }
        }
    
    def _get_recommendations(self, score: int, issues: List[Dict]) -> List[str]:
        """Generate non-AI recommendations based on issues and score."""
        recommendations = []
        
        # Add critical issues as recommendations
        for issue in issues:
            if issue.get("level") == "critical":
                recommendations.append(issue.get("detail", ""))
        
        # Add strategic recommendations based on score
        if score < 50:
            recommendations.append("Create a comprehensive GMB optimization strategy")
            recommendations.append("Prioritize addressing critical profile gaps first")
        elif score < 70:
            recommendations.append("Focus on building review momentum")
            recommendations.append("Establish a consistent content posting schedule")
        elif score < 85:
            recommendations.append("Expand your photo library with high-quality images")
            recommendations.append("Implement customer engagement strategies")
        else:
            recommendations.append("Maintain consistent posting and engagement")
            recommendations.append("Encourage satisfied customers to leave reviews")
        
        return recommendations[:6]  # Limit to 6

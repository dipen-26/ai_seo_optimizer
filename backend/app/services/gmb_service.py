"""GMB Service with validation and data quality checks."""
from typing import Dict, Any, Optional, List
from ..utils.validators import validate_business_name
from ..utils.gmb_data_extractor import GMBDataExtractor
from ..services.gmb_scoring_service import GMBScoringEngine
from ..services.ai_service import AIService


class GMBService:
    """GMB audit service with data validation."""
    
    def __init__(self):
        self.ai_service = AIService()
    
    async def audit_business(
        self,
        business_name: str,
        address: Optional[str] = None,
        category: Optional[str] = None
    ) -> Dict[str, Any]:
        """Perform GMB audit with validation."""
        
        # Step 1: Validate
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
        
        # Step 2: Extract data
        extractor = GMBDataExtractor(business_name, address)
        extracted_data = await extractor.extract_all()
        
        # Step 3: Validate extracted data
        validation_result = self._validate_data(extracted_data)
        
        # Step 4: Score
        scorer = GMBScoringEngine(extracted_data)
        score, issues, breakdown = scorer.calculate_score()
        
        # Add validation warnings as issues if data looks wrong
        if validation_result["has_issues"]:
            issues.extend(validation_result["issues"])
        
        # Step 5: AI recommendations
        ai_suggestions = await self.ai_service.generate_gmb_recommendations(
            score=score,
            business_name=business_name,
            location=address or extracted_data.get("location", "Not specified"),
            extracted_data=extracted_data,
            issues=issues,
            data_source=extracted_data.get("data_source", "unknown")
        )
        
        # Step 6: Generate recommendations
        recommendations = self._get_recommendations(score, issues)
        
        # Build response
        response = {
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
                "website": extracted_data.get("profile_data", {}).get("website", ""),
                "address": extracted_data.get("profile_data", {}).get("address", ""),
                "hours": extracted_data.get("profile_data", {}).get("hours", {}),
                "description": extracted_data.get("profile_data", {}).get("description", "")
            },
            "data_source": extracted_data.get("data_source", "unknown"),
            "data_note": extracted_data.get("data_note", "")
        }
        
        # Add validation warning if data extraction failed
        if validation_result["has_issues"]:
            response["warning"] = validation_result["warning"]
            response["extraction_status"] = "partial"
        else:
            response["extraction_status"] = "complete"
        
        return response
    
    def _validate_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate extracted data to ensure quality.
        
        Returns validation result with issues if data seems wrong.
        """
        import re
        issues = []
        has_issues = False
        warning = ""
        
        profile = data.get("profile_data", {})
        review_data = data.get("review_data", {})
        content_metrics = data.get("content_metrics", {})
        data_source = data.get("data_source", "unknown")
        
        # Check 1: If reviews = 0 but rating > 0 (impossible)
        if review_data.get("average_rating", 0) > 0 and review_data.get("total_reviews", 0) == 0:
            has_issues = True
            warning = "Data extraction may be incomplete - rating found but no review count"
            issues.append({
                "level": "error",
                "severity": "high",
                "title": "Incomplete review data",
                "detail": "A rating is present but the review count is zero. This indicates a critical extraction failure for review data.",
                "penalty": 0,
                "error_code": "reviews_missing"
            })
        
        # Check 2: If rating = 0 but reviews > 0 (also impossible)
        if review_data.get("total_reviews", 0) > 0 and review_data.get("average_rating", 0) == 0:
            has_issues = True
            warning = "Data extraction may be incomplete - reviews found but no rating"
            issues.append({
                "level": "error",
                "severity": "high",
                "title": "Incomplete rating data",
                "detail": "Review count is greater than zero but the rating is zero. This indicates a critical extraction failure for rating data.",
                "penalty": 0,
                "error_code": "rating_missing"
            })
        
        # Check 3: All zeros with mock data (extraction failed)
        if data_source in ["mock", "estimated"]:
            has_issues = True
            warning = "Estimated data based on business type - search engines blocked scraping"
            issues.append({
                "level": "error",
                "severity": "critical",
                "title": "Using estimated data",
                "detail": "Could not extract real data from Google/Yelp. Results are estimated based on business type. To get real data: (1) Add SerpAPI key, or (2) Run on Linux where Playwright works.",
                "penalty": 0,
                "error_code": "extraction_failed_estimated"
            })
        
        # Check 4: Missing core profile data
        if not profile.get("phone") and not profile.get("website") and not profile.get("address"):
            has_issues = True
            if not warning:
                warning = "Limited profile data extracted"
            # This might be a legitimate state for a new or incomplete profile, so a warning is better than an error.
            issues.append({
                "level": "warning",
                "severity": "medium",
                "title": "Missing Core Profile Data",
                "detail": "The business phone, website, and address are all missing. The profile is likely incomplete or data was not extracted correctly.",
                "penalty": 0,
                "error_code": "core_profile_data_missing"
            })

        # Check 5: Placeholder phone number detected
        phone = profile.get("phone", "")
        if phone and re.search(r'\(555\)|000-0000', phone):
            has_issues = True
            warning = "Placeholder phone number detected. Real data was not extracted."
            issues.append({
                "level": "error",
                "severity": "critical",
                "title": "Placeholder Phone Number",
                "detail": f"The phone number '{phone}' appears to be a placeholder. The real phone number was not extracted.",
                "penalty": 0,
                "error_code": "placeholder_phone"
            })
        
        return {
            "has_issues": has_issues,
            "issues": issues,
            "warning": warning
        }
    
    def _get_recommendations(self, score: int, issues: List[Dict]) -> List[str]:
        """Generate recommendations based on issues."""
        recommendations = []
        
        for issue in issues:
            if issue.get("level") in ["critical", "high"]:
                recommendations.append(issue.get("detail", ""))
        
        if score < 50:
            recommendations.append("Complete your GMB profile with all required information")
            recommendations.append("Verify data extraction - results may be incomplete")
        elif score < 70:
            recommendations.append("Focus on building review momentum")
            recommendations.append("Establish a consistent content posting schedule")
        elif score < 85:
            recommendations.append("Expand your photo library with high-quality images")
            recommendations.append("Implement customer engagement strategies")
        else:
            recommendations.append("Maintain consistent posting and engagement")
            recommendations.append("Encourage satisfied customers to leave reviews")
        
        return recommendations[:6]

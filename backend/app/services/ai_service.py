"""AI Service for generating recommendations."""
import json
import httpx
from typing import Dict, Any, Optional, List
from ..core.config import OPENAI_API_KEY, AI_MODEL, AI_BASE_URL, HTTP_TIMEOUT


class AIService:
    """Service for AI-powered recommendations."""
    
    def __init__(self):
        """Initialize AI service."""
        self.api_key = OPENAI_API_KEY
        self.model = AI_MODEL
        self.base_url = AI_BASE_URL
        self.client = None
    
    async def generate_cro_recommendations(
        self,
        score: int,
        extracted_data: Dict[str, Any],
        issues: List[Dict[str, str]],
        goal: Optional[str] = None
    ) -> Optional[List[str]]:
        """
        Generate CRO recommendations using AI.
        
        Args:
            score: Current CRO score
            extracted_data: Extracted page data
            issues: List of identified issues
            goal: Primary conversion goal
            
        Returns:
            List of AI-generated recommendations
        """
        if not self.api_key:
            return self._get_fallback_recommendations(score, issues)
        
        prompt = self._build_cro_prompt(score, extracted_data, issues, goal)
        
        try:
            async with httpx.AsyncClient(timeout=HTTP_TIMEOUT) as client:
                response = await client.post(
                    f"{self.base_url}/chat/completions",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": self.model,
                        "messages": [
                            {"role": "system", "content": "You are an expert CRO specialist."},
                            {"role": "user", "content": prompt}
                        ],
                        "temperature": 0.7,
                        "max_tokens": 500
                    }
                )
                
                if response.status_code == 200:
                    data = response.json()
                    content = data["choices"][0]["message"]["content"]
                    return self._parse_recommendations(content)
        except Exception as e:
            print(f"AI Service error: {e}")
        
        return self._get_fallback_recommendations(score, issues)
    
    def _build_cro_prompt(
        self,
        score: int,
        extracted_data: Dict[str, Any],
        issues: List[Dict[str, str]],
        goal: Optional[str] = None
    ) -> str:
        """Build the prompt for CRO recommendations."""
        issues_text = "\n".join([f"- {i.get('title')}: {i.get('detail')}" for i in issues[:5]])
        
        prompt = f"""
Analyze this CRO audit and provide 5-8 specific, actionable recommendations.

Current Score: {score}/100
Conversion Goal: {goal or 'Not specified'}
Page Title: {extracted_data.get('title', 'N/A')}
H1: {extracted_data.get('h1_tags', ['N/A'])[0] if extracted_data.get('h1_tags') else 'N/A'}
Meta Description: {extracted_data.get('meta_description', 'N/A')}

Top Issues Found:
{issues_text}

Please provide recommendations as a numbered list. Be specific and actionable.
Format each as: "Number. Short title - detailed explanation"
"""
        return prompt.strip()
    
    def _parse_recommendations(self, content: str) -> List[str]:
        """Parse AI response into recommendations."""
        lines = content.split("\n")
        recommendations = []
        
        for line in lines:
            line = line.strip()
            # Remove numbering
            if line and line[0].isdigit():
                line = line.split(".", 1)[-1].strip()
            
            if line:
                recommendations.append(line)
        
        return recommendations[:8]  # Limit to 8
    
    def _get_fallback_recommendations(
        self,
        score: int,
        issues: List[Dict[str, str]]
    ) -> List[str]:
        """Get fallback recommendations when AI is unavailable."""
        recommendations = []
        
        for issue in issues:
            title = issue.get("title", "")
            detail = issue.get("detail", "")
            if detail:
                recommendations.append(f"{title} - {detail}")
        
        # Add generic recommendations based on score
        if score < 50:
            recommendations.append("Complete a full CRO audit and prioritize critical issues")
            recommendations.append("Run A/B tests on your primary CTAs")
        elif score < 75:
            recommendations.append("Focus on conversion funnel optimization")
            recommendations.append("Implement heat mapping to understand user behavior")
        else:
            recommendations.append("Consider advanced personalization techniques")
            recommendations.append("Implement progressive profiling for lead forms")
        
        return recommendations[:8]  # Limit to 8
    
    async def generate_gmb_recommendations(
        self,
        score: int,
        business_name: str,
        location: str,
        extracted_data: Dict[str, Any],
        issues: List[Dict[str, str]]
    ) -> Optional[List[str]]:
        """
        Generate GMB recommendations using AI.
        
        Args:
            score: Current GMB score
            business_name: Name of the business
            location: Business location
            extracted_data: Extracted GMB data
            issues: List of identified issues
            
        Returns:
            List of AI-generated recommendations
        """
        if not self.api_key:
            return self._get_fallback_gmb_recommendations(score, issues)
        
        prompt = self._build_gmb_prompt(score, business_name, location, extracted_data, issues)
        
        try:
            async with httpx.AsyncClient(timeout=HTTP_TIMEOUT) as client:
                response = await client.post(
                    f"{self.base_url}/chat/completions",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": self.model,
                        "messages": [
                            {"role": "system", "content": "You are an expert local SEO and Google My Business specialist."},
                            {"role": "user", "content": prompt}
                        ],
                        "temperature": 0.7,
                        "max_tokens": 600
                    }
                )
                
                if response.status_code == 200:
                    data = response.json()
                    content = data["choices"][0]["message"]["content"]
                    return self._parse_recommendations(content)
        except Exception as e:
            print(f"AI Service GMB error: {e}")
        
        return self._get_fallback_gmb_recommendations(score, issues)
    
    def _build_gmb_prompt(
        self,
        score: int,
        business_name: str,
        location: str,
        extracted_data: Dict[str, Any],
        issues: List[Dict[str, str]]
    ) -> str:
        """Build the prompt for GMB recommendations."""
        profile = extracted_data.get("profile_data", {})
        review_data = extracted_data.get("review_data", {})
        metrics = extracted_data.get("content_metrics", {})
        
        issues_text = "\n".join([f"- {i.get('title')}: {i.get('detail')}" for i in issues[:6]])
        
        prompt = f"""
Analyze this Google My Business profile audit and provide a comprehensive local SEO strategy with 6-8 specific, actionable recommendations.

BUSINESS PROFILE
Name: {business_name}
Location: {location}
Current GMB Score: {score}/100

CURRENT METRICS
- Rating: {review_data.get('average_rating', 0)}⭐ ({review_data.get('total_reviews', 0)} reviews)
- Photos: {metrics.get('photo_count', 0)}
- Posts: {metrics.get('post_count', 0)}
- Website: {profile.get('website', 'Not linked')}
- Phone: {profile.get('phone', 'Not provided')}

TOP ISSUES
{issues_text}

Based on this profile, provide:
1. A 6-point local SEO strategy for improving visibility
2. Review management and response strategy
3. Content posting strategy (frequency & type)
4. Photo/media enhancements
5. Local keyword optimization suggestions
6. Engagement metrics improvement plan

Format as a numbered list. Be specific and actionable, focusing on quick wins first.
"""
        return prompt.strip()
    
    def _get_fallback_gmb_recommendations(
        self,
        score: int,
        issues: List[Dict[str, str]]
    ) -> List[str]:
        """Get fallback GMB recommendations when AI is unavailable."""
        recommendations = []
        
        for issue in issues[:3]:
            detail = issue.get("detail", "")
            if detail:
                recommendations.append(detail)
        
        # Add generic recommendations based on score
        if score < 50:
            recommendations.append("Complete your GMB profile with all required information")
            recommendations.append("Encourage customers to leave reviews on your GMB profile")
        elif score < 70:
            recommendations.append("Post 2-3 times per week on your GMB profile")
            recommendations.append("Add 10+ high-quality photos of your business and services")
        elif score < 85:
            recommendations.append("Expand your photo library with customer testimonials")
            recommendations.append("Respond to all customer reviews within 24 hours")
        else:
            recommendations.append("Monitor local search performance metrics regularly")
            recommendations.append("Encourage customer check-ins and interactions")
        
        return recommendations[:8]  # Limit to 8

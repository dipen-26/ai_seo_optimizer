"""AI Service for generating recommendations with rich page context."""
import json
import httpx
import os
from typing import Dict, Any, Optional, List
from ..core.config import OPENROUTER_API_KEY, OPENAI_API_KEY, AI_MODEL, HTTP_TIMEOUT, USE_OPENROUTER


class AIService:
    """Service for AI-powered recommendations."""
    
    def __init__(self):
        """Initialize AI service."""
        # Use OpenRouter if available, otherwise use OpenAI
        if OPENROUTER_API_KEY:
            self.api_key = OPENROUTER_API_KEY
            self.base_url = "https://openrouter.ai/api/v1"
            self.use_openrouter = True
        else:
            self.api_key = OPENAI_API_KEY
            self.base_url = os.getenv("AI_BASE_URL", "https://api.openai.com/v1")
            self.use_openrouter = False
        self.model = AI_MODEL
        self.client = None
    
    async def generate_cro_recommendations(
        self,
        score: int,
        extracted_data: Dict[str, Any],
        issues: List[Dict[str, str]],
        goal: Optional[str] = None,
        industry: Optional[str] = "default",
        pagespeed_data: Optional[Dict[str, Any]] = None,
        viewport_data: Optional[Dict[str, Any]] = None
    ) -> Optional[List[str]]:
        """
        Generate CRO recommendations using AI with rich page context.
        
        Args:
            score: Current CRO score
            extracted_data: Extracted page data (with real content)
            issues: List of identified issues
            goal: Primary conversion goal
            industry: Industry type for context
            pagespeed_data: Google PageSpeed data
            viewport_data: Above-the-fold CTA data
            
        Returns:
            List of AI-generated recommendations
        """
        if not self.api_key:
            return self._get_fallback_recommendations(score, issues)
        
        prompt = self._build_cro_prompt(
            score, extracted_data, issues, goal, industry, 
            pagespeed_data, viewport_data
        )
        
        try:
            async with httpx.AsyncClient(timeout=HTTP_TIMEOUT) as client:
                # OpenRouter requires additional headers
                headers = {
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                }
                if hasattr(self, 'use_openrouter') and self.use_openrouter:
                    headers["HTTP-Referer"] = "https://ai-seo-optimizer.com"
                    headers["X-Title"] = "AI SEO Optimizer"
                
                response = await client.post(
                    f"{self.base_url}/chat/completions",
                    headers=headers,
                    json={
                        "model": self.model,
                        "messages": [
                            {"role": "system", "content": "You are an expert CRO specialist with deep knowledge of conversion optimization, A/B testing, and user psychology."},
                            {"role": "user", "content": prompt}
                        ],
                        "temperature": 0.7,
                        "max_tokens": 800
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
        goal: Optional[str],
        industry: str,
        pagespeed_data: Optional[Dict[str, Any]],
        viewport_data: Optional[Dict[str, Any]]
    ) -> str:
        """Build the prompt for CRO recommendations with real page content."""
        
        # Extract actual page content for the prompt
        title = extracted_data.get("title", "Not found")
        h1_tags = extracted_data.get("h1_tags", [])
        h1_text = h1_tags[0] if h1_tags else "Not found"
        meta_desc = extracted_data.get("meta_description", "Not found")
        
        # Buttons/CTAs
        buttons = extracted_data.get("buttons", [])
        button_texts = [b.get("text", "") for b in buttons[:5]]
        
        # Trust signals
        trust_signals = extracted_data.get("trust_signals", {})
        schema_data = extracted_data.get("schema", {})
        schema_types = schema_data.get("schema_types", [])
        
        # Format issues
        issues_text = "\n".join([
            f"- {i.get('title', 'Unknown')}: {i.get('detail', '')}" 
            for i in issues[:6]
        ])
        
        # Build PageSpeed context
        ps_context = ""
        if pagespeed_data:
            lcp = pagespeed_data.get("lcp", 0)
            fid = pagespeed_data.get("fid", 0)
            cls = pagespeed_data.get("cls", 0)
            ps_score = pagespeed_data.get("score", 0)
            ps_context = f"""
PAGESPEED METRICS:
- Performance Score: {ps_score}/100
- Largest Contentful Paint: {lcp:.1f}s
- First Input Delay: {fid:.0f}ms
- Cumulative Layout Shift: {cls:.2f}
"""
        
        # Build viewport context
        vp_context = ""
        if viewport_data:
            cta_above = viewport_data.get("cta_above_fold_count", 0)
            cta_below = viewport_data.get("cta_below_fold_count", 0)
            has_above = viewport_data.get("has_cta_above_fold", False)
            vp_context = f"""
ABOVE-THE-FOLD ANALYSIS:
- Has CTA above fold: {has_above}
- CTAs in viewport: {cta_above}
- CTAs below fold: {cta_below}
"""
        
        prompt = f"""Analyze this CRO audit and provide 5-8 specific, actionable recommendations.

CURRENT SCORE: {score}/100
INDUSTRY: {industry}
CONVERSION GOAL: {goal or 'Not specified'}

ACTUAL PAGE CONTENT:
- Page Title: "{title}"
- H1 Tag: "{h1_text}"
- Meta Description: "{meta_desc}"
- CTA Buttons Found: {button_texts}
- Number of CTAs: {len(buttons)}

TRUST SIGNALS DETECTED:
- HTTPS/SSL: {trust_signals.get('is_https', False)}
- Schema Types: {schema_types or 'None'}
- Third-party Reviews: {trust_signals.get('third_party_reviews', [])}
- Security Badges: {trust_signals.get('security_badges', [])}

{ps_context}

{vp_context}

ISSUES FOUND:
{issues_text}

Please provide recommendations as a numbered list. Be specific and actionable, referencing the ACTUAL content above. For each recommendation:
1. Reference specific elements from the page content
2. Explain the CRO principle behind the recommendation
3. Provide concrete implementation steps

Format: "Number. Title - Detailed explanation"
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
        issues: List[Dict[str, str]],
        data_source: str = "serpapi"
    ) -> Optional[List[str]]:
        """
        Generate GMB recommendations using AI.
        
        Args:
            score: Current GMB score
            business_name: Name of the business
            location: Business location
            extracted_data: Extracted GMB data (REAL data from SerpAPI)
            issues: List of identified issues
            data_source: Source of the data (serpapi, mock)
            
        Returns:
            List of AI-generated recommendations
        """
        if not self.api_key:
            return self._get_fallback_gmb_recommendations(score, issues)
        
        prompt = self._build_gmb_prompt(
            score, business_name, location, extracted_data, issues, data_source
        )
        
        try:
            async with httpx.AsyncClient(timeout=HTTP_TIMEOUT) as client:
                # OpenRouter requires additional headers
                headers = {
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                }
                if self.use_openrouter:
                    headers["HTTP-Referer"] = "https://ai-seo-optimizer.com"
                    headers["X-Title"] = "AI SEO Optimizer"
                
                response = await client.post(
                    f"{self.base_url}/chat/completions",
                    headers=headers,
                    json={
                        "model": self.model,
                        "messages": [
                            {"role": "system", "content": "You are an expert local SEO and Google My Business specialist with deep knowledge of local search optimization."},
                            {"role": "user", "content": prompt}
                        ],
                        "temperature": 0.7,
                        "max_tokens": 800
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
        issues: List[Dict[str, str]],
        data_source: str
    ) -> str:
        """Build the prompt for GMB recommendations with real data."""
        profile = extracted_data.get("profile_data", {})
        review_data = extracted_data.get("review_data", {})
        metrics = extracted_data.get("content_metrics", {})
        
        issues_text = "\n".join([
            f"- {i.get('title', 'Unknown')}: {i.get('detail', '')}" 
            for i in issues[:6]
        ])
        
        # Note data source
        data_note = "Data obtained from Google Maps (SerpAPI)" if data_source == "serpapi" else "Data based on analysis"
        
        prompt = f"""Analyze this Google My Business profile audit and provide a comprehensive local SEO strategy with 6-8 specific, actionable recommendations.

BUSINESS PROFILE
- Name: {business_name}
- Location: {location}
- Data Source: {data_note}
- Current GMB Score: {score}/100

REAL METRICS (from Google):
- Rating: {review_data.get('average_rating', 0)} stars ({review_data.get('total_reviews', 0)} reviews)
- Recent Reviews (30 days): {review_data.get('reviews_last_30_days', 0)}
- Photos: {metrics.get('photo_count', 0)}
- Videos: {metrics.get('video_count', 0)}
- Posts: {metrics.get('post_count', 0)}
- Recent Posts: {metrics.get('posts_last_30_days', 0)}
- Website: {profile.get('website', 'Not linked')}
- Phone: {profile.get('phone', 'Not provided')}
- Categories: {profile.get('categories', [])}
- Hours: {'Complete' if profile.get('hours') else 'Incomplete'}

TOP ISSUES:
{issues_text}

Based on this REAL data, provide:
1. Priority actions for quick wins
2. Review management strategy based on actual review count
3. Content posting recommendations based on actual post frequency
4. Photo enhancement suggestions based on actual photo count
5. Local keyword optimization specific to this business
6. Engagement improvement plan

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

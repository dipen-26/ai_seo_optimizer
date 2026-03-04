"""CRO Scoring Engine."""
from typing import Dict, Any, Tuple
from ..utils.data_extractor import CRODataExtractor


class CROScoringEngine:
    """
    Score CRO elements based on best practices.
    
    Scoring Weights:
    - CTA Presence: 20%
    - Headlines: 15%
    - Forms: 20%
    - Trust Signals: 15%
    - Content Clarity: 30%
    """
    
    # Maximum points per category
    WEIGHTS = {
        "cta": 20,
        "headlines": 15,
        "forms": 20,
        "trust_signals": 15,
        "content_clarity": 30
    }
    
    def __init__(self, extracted_data: Dict[str, Any]):
        """Initialize with extracted CRO data."""
        self.data = extracted_data
        self.issues = []
        self.score_breakdown = {}
    
    def score_cta(self) -> Tuple[float, list]:
        """
        Score CTA presence and quality.
        Returns (score, issues)
        """
        buttons = self.data.get("buttons", [])
        issues = []
        
        if not buttons:
            issues.append({
                "level": "critical",
                "title": "No CTA buttons found",
                "detail": "Conversion pages should have clear call-to-action buttons."
            })
            return 0, issues
        
        # Check for action-oriented CTAs
        weak_ctras = ["click here", "submit", "ok", "button"]
        weak_count = sum(1 for b in buttons if b.get("text", "").lower() in weak_ctras)
        
        if weak_count == len(buttons):
            issues.append({
                "level": "improve",
                "title": "Weak CTA copy",
                "detail": "Use action-oriented verbs like 'Get Started', 'Sign Up', 'Claim', 'Download'."
            })
            return 10, issues
        
        return 20, issues
    
    def score_headlines(self) -> Tuple[float, list]:
        """
        Score headline presence and structure.
        Returns (score, issues)
        """
        h1_tags = self.data.get("h1_tags", [])
        issues = []
        
        # Check for H1
        if not h1_tags:
            issues.append({
                "level": "critical",
                "title": "Missing H1 tag",
                "detail": "Every page should have exactly one H1 tag for SEO and accessibility."
            })
            return 5, issues
        
        if len(h1_tags) > 1:
            issues.append({
                "level": "improve",
                "title": f"Multiple H1 tags ({len(h1_tags)} found)",
                "detail": "Best practice is to have exactly one H1 per page. Consider restructuring."
            })
            return 10, issues
        
        # Check H1 length
        h1_text = h1_tags[0]
        if len(h1_text) < 10:
            issues.append({
                "level": "improve",
                "title": "H1 is too short",
                "detail": "H1 should be descriptive and 10-70 characters for best impact."
            })
            return 10, issues
        
        return 15, issues
    
    def score_forms(self) -> Tuple[float, list]:
        """
        Score form presence and structure.
        Returns (score, issues)
        """
        forms = self.data.get("forms", [])
        issues = []
        
        if not forms:
            # Not all pages need forms
            return 20, issues
        
        for idx, form in enumerate(forms):
            fields = form.get("fields", [])
            
            # Check for reasonable field count
            if len(fields) > 8:
                issues.append({
                    "level": "improve",
                    "title": f"Form {idx+1} has too many fields",
                    "detail": "Long forms reduce conversion rates. Aim for 3-5 key fields."
                })
            
            if not fields:
                issues.append({
                    "level": "improve",
                    "title": f"Form {idx+1} has no fields",
                    "detail": "Form structure seems incomplete."
                })
        
        return 20 if not issues else 12, issues
    
    def score_trust_signals(self) -> Tuple[float, list]:
        """
        Score trust signals like testimonials, certifications, etc.
        Returns (score, issues)
        """
        html_text = ""  # Simplified for MVP
        issues = []
        
        # Look for trust-related keywords in page
        trust_keywords = ["testimonial", "review", "client", "trust", "secure", "ssl", "certified"]
        # This is a simplified check - in production, use more sophisticated NLP
        
        issues.append({
            "level": "improve",
            "title": "Limited trust signals",
            "detail": "Add testimonials, client logos, certifications, or security badges to build trust."
        })
        
        return 10, issues
    
    def score_content_clarity(self) -> Tuple[float, list]:
        """
        Score content structure and clarity.
        Returns (score, issues)
        """
        meta_desc = self.data.get("meta_description")
        h1_tags = self.data.get("h1_tags", [])
        headings = self.data.get("headings", {})
        images = self.data.get("images", [])
        
        issues = []
        base_score = 30
        
        # Check meta description
        if not meta_desc:
            issues.append({
                "level": "critical",
                "title": "Missing meta description",
                "detail": "Add a compelling 120-155 character meta description for better CTR in search results."
            })
            base_score -= 10
        elif len(meta_desc) < 120 or len(meta_desc) > 155:
            issues.append({
                "level": "improve",
                "title": "Meta description length not optimal",
                "detail": f"Current: {len(meta_desc)} chars. Ideal: 120-155 characters."
            })
            base_score -= 5
        
        # Check for hierarchy
        if len(headings) < 2:
            issues.append({
                "level": "improve",
                "title": "Weak heading structure",
                "detail": "Use clear H2-H6 hierarchy to guide readers through content."
            })
            base_score -= 5
        
        # Check images
        total_images = len(images)
        if total_images > 0:
            images_without_alt = sum(1 for img in images if not img.get("has_alt"))
            if images_without_alt > 0:
                issues.append({
                    "level": "improve",
                    "title": f"{images_without_alt}/{total_images} images missing alt text",
                    "detail": "Alt text improves accessibility and SEO. Add descriptive alt for every image."
                })
                base_score -= 3
        
        return max(0, base_score), issues
    
    def calculate_score(self) -> Tuple[int, list]:
        """
        Calculate overall CRO score (0-100).
        Returns (score, combined_issues)
        """
        all_issues = []
        
        # Score each component
        cta_score, cta_issues = self.score_cta()
        all_issues.extend(cta_issues)
        
        headline_score, headline_issues = self.score_headlines()
        all_issues.extend(headline_issues)
        
        form_score, form_issues = self.score_forms()
        all_issues.extend(form_issues)
        
        trust_score, trust_issues = self.score_trust_signals()
        all_issues.extend(trust_issues)
        
        content_score, content_issues = self.score_content_clarity()
        all_issues.extend(content_issues)
        
        # Store breakdown
        self.score_breakdown = {
            "cta": cta_score,
            "headlines": headline_score,
            "forms": form_score,
            "trust_signals": trust_score,
            "content_clarity": content_score
        }
        
        # Calculate total
        total_score = int(cta_score + headline_score + form_score + trust_score + content_score)
        
        # Limit to 100
        total_score = min(100, max(0, total_score))
        
        self.issues = all_issues
        
        return total_score, all_issues

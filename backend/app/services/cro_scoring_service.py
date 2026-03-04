"""CRO Scoring Engine with industry-specific weights and severity scoring."""
from typing import Dict, Any, Tuple, Optional
from ..utils.data_extractor import CRODataExtractor


# Industry-specific weight profiles
WEIGHT_PROFILES = {
    "saas": {
        "cta": 25,
        "headlines": 10,
        "forms": 25,
        "trust_signals": 15,
        "content_clarity": 15,
        "performance": 10
    },
    "restaurant": {
        "cta": 15,
        "headlines": 10,
        "forms": 10,
        "trust_signals": 15,
        "content_clarity": 20,
        "performance": 15,
        "photos": 15
    },
    "ecommerce": {
        "cta": 25,
        "headlines": 10,
        "forms": 15,
        "trust_signals": 25,
        "content_clarity": 10,
        "performance": 15
    },
    "healthcare": {
        "cta": 15,
        "headlines": 15,
        "forms": 20,
        "trust_signals": 25,
        "content_clarity": 15,
        "performance": 10
    },
    "real_estate": {
        "cta": 20,
        "headlines": 15,
        "forms": 15,
        "trust_signals": 20,
        "content_clarity": 15,
        "performance": 15
    },
    "default": {
        "cta": 20,
        "headlines": 15,
        "forms": 20,
        "trust_signals": 15,
        "content_clarity": 20,
        "performance": 10
    }
}

# Issue severity penalties (subtracted from 100)
SEVERITY_PENALTIES = {
    "critical": 15,
    "high": 10,
    "medium": 5,
    "improve": 3,
    "info": 1
}


class CROScoringEngine:
    """
    Score CRO elements based on best practices with industry-specific weights.
    
    Default Weights (can be overridden by industry):
    - CTA Presence: 20%
    - Headlines: 15%
    - Forms: 20%
    - Trust Signals: 15%
    - Content Clarity: 20%
    - Performance: 10%
    """
    
    def __init__(self, extracted_data: Dict[str, Any], industry: str = "default", pagespeed_data: Optional[Dict[str, Any]] = None):
        """Initialize with extracted CRO data."""
        self.data = extracted_data
        self.industry = industry.lower() if industry else "default"
        self.pagespeed_data = pagespeed_data
        self.issues = []
        self.score_breakdown = {}
        
        # Get industry-specific weights
        if self.industry in WEIGHT_PROFILES:
            self.weights = WEIGHT_PROFILES[self.industry]
        else:
            self.weights = WEIGHT_PROFILES["default"]
    
    def score_cta(self) -> Tuple[float, list]:
        """
        Score CTA presence, quality, and positioning.
        Returns (score, issues)
        """
        buttons = self.data.get("buttons", [])
        cta_positions = self.data.get("cta_positions", {})
        issues = []
        
        # Get max points for this category
        max_points = self.weights.get("cta", 20)
        
        if not buttons:
            issues.append({
                "level": "critical",
                "severity": "critical",
                "title": "No CTA buttons found",
                "detail": "Conversion pages should have clear call-to-action buttons.",
                "penalty": SEVERITY_PENALTIES["critical"]
            })
            return 0, issues
        
        # Check for action-oriented CTAs
        weak_ctras = ["click here", "submit", "ok", "button", "go"]
        action_ctras = ["get started", "sign up", "claim", "download", "free", "try", 
                       "buy", "order", "book", "schedule", "contact", "demo", "learn more",
                       "get quote", "request", "subscribe", "join", "start", "create"]
        
        button_texts = [b.get("text", "").lower() for b in buttons]
        
        weak_count = sum(1 for text in button_texts if text in weak_ctras)
        action_count = sum(1 for text in button_texts if any(cta in text for cta in action_ctras))
        
        # Score based on CTA quality
        if weak_count == len(buttons):
            issues.append({
                "level": "high",
                "severity": "high",
                "title": "Weak CTA copy",
                "detail": "Use action-oriented verbs like 'Get Started', 'Sign Up', 'Claim', 'Download'.",
                "penalty": SEVERITY_PENALTIES["high"]
            })
            return max_points * 0.3, issues
        
        if action_count == 0:
            issues.append({
                "level": "improve",
                "severity": "improve",
                "title": "CTA copy could be stronger",
                "detail": "Consider using more action-oriented CTA phrases.",
                "penalty": SEVERITY_PENALTIES["improve"]
            })
            return max_points * 0.7, issues
        
        # Bonus for multiple CTAs
        if len(buttons) >= 2:
            return max_points, issues
        
        return max_points * 0.85, issues
    
    def score_headlines(self) -> Tuple[float, list]:
        """
        Score headline presence and structure.
        Returns (score, issues)
        """
        h1_tags = self.data.get("h1_tags", [])
        issues = []
        
        max_points = self.weights.get("headlines", 15)
        
        # Check for H1
        if not h1_tags:
            issues.append({
                "level": "critical",
                "severity": "critical",
                "title": "Missing H1 tag",
                "detail": "Every page should have exactly one H1 tag for SEO and accessibility.",
                "penalty": SEVERITY_PENALTIES["critical"]
            })
            return 0, issues
        
        if len(h1_tags) > 1:
            issues.append({
                "level": "improve",
                "severity": "improve",
                "title": f"Multiple H1 tags ({len(h1_tags)} found)",
                "detail": "Best practice is to have exactly one H1 per page. Consider restructuring.",
                "penalty": SEVERITY_PENALTIES["improve"]
            })
            return max_points * 0.6, issues
        
        # Check H1 length
        h1_text = h1_tags[0]
        if len(h1_text) < 10:
            issues.append({
                "level": "improve",
                "severity": "improve",
                "title": "H1 is too short",
                "detail": "H1 should be descriptive and 10-70 characters for best impact.",
                "penalty": SEVERITY_PENALTIES["improve"]
            })
            return max_points * 0.6, issues
        
        if len(h1_text) > 70:
            issues.append({
                "level": "improve",
                "severity": "improve",
                "title": "H1 is too long",
                "detail": f"Current: {len(h1_text)} chars. Keep H1 under 70 characters.",
                "penalty": SEVERITY_PENALTIES["improve"]
            })
            return max_points * 0.8, issues
        
        return max_points, issues
    
    def score_forms(self) -> Tuple[float, list]:
        """
        Score form presence and structure.
        Returns (score, issues)
        """
        forms = self.data.get("forms", [])
        issues = []
        
        max_points = self.weights.get("forms", 20)
        
        if not forms:
            # Not all pages need forms - give partial credit
            return max_points * 0.7, issues
        
        for idx, form in enumerate(forms):
            fields = form.get("fields", [])
            
            # Check for reasonable field count
            if len(fields) > 8:
                issues.append({
                    "level": "improve",
                    "severity": "improve",
                    "title": f"Form {idx+1} has too many fields",
                    "detail": "Long forms reduce conversion rates. Aim for 3-5 key fields.",
                    "penalty": SEVERITY_PENALTIES["improve"]
                })
            
            if not fields:
                issues.append({
                    "level": "high",
                    "severity": "high",
                    "title": f"Form {idx+1} has no fields",
                    "detail": "Form structure seems incomplete.",
                    "penalty": SEVERITY_PENALTIES["high"]
                })
        
        if issues:
            return max_points * 0.6, issues
        
        return max_points, issues
    
    def score_trust_signals(self) -> Tuple[float, list]:
        """
        Score trust signals using structured detection (not keyword guessing).
        Returns (score, issues)
        """
        trust_data = self.data.get("trust_signals", {})
        schema_data = self.data.get("schema", {})
        issues = []
        
        max_points = self.weights.get("trust_signals", 15)
        
        # Calculate trust from structured data
        score = 0
        max_score = 10
        
        # 1. HTTPS/SSL (2 points)
        if trust_data.get("is_https", False):
            score += 2
        
        # 2. Schema markup presence (3 points)
        if schema_data.get("has_schema", False):
            score += 3
        
        # 3. Review schema (2 points)
        if schema_data.get("trust_signals", {}).get("has_review_schema", False):
            score += 2
        
        # 4. Aggregate rating schema (2 points)
        if schema_data.get("trust_signals", {}).get("has_aggregate_rating", False):
            score += 2
        
        # 5. Third-party reviews (1 point)
        if trust_data.get("third_party_reviews"):
            score += 1
        
        # Convert to max_points
        trust_score = (score / max_score) * max_points
        
        # Generate issues based on missing signals
        if not trust_data.get("is_https"):
            issues.append({
                "level": "critical",
                "severity": "critical",
                "title": "Site is not using HTTPS",
                "detail": "SSL certificate is essential for trust and SEO.",
                "penalty": SEVERITY_PENALTIES["critical"]
            })
        
        if not schema_data.get("has_schema"):
            issues.append({
                "level": "high",
                "severity": "high",
                "title": "No structured data (Schema.org) found",
                "detail": "Add JSON-LD structured data for better search visibility and trust signals.",
                "penalty": SEVERITY_PENALTIES["high"]
            })
        
        if not schema_data.get("trust_signals", {}).get("has_review_schema") and not schema_data.get("trust_signals", {}).get("has_aggregate_rating"):
            issues.append({
                "level": "improve",
                "severity": "improve",
                "title": "No review/rating schema found",
                "detail": "Add Review or AggregateRating schema markup to display star ratings in search.",
                "penalty": SEVERITY_PENALTIES["improve"]
            })
        
        if not trust_data.get("third_party_reviews"):
            issues.append({
                "level": "improve",
                "severity": "improve",
                "title": "No third-party review badges detected",
                "detail": "Add trust badges from Trustpilot, G2, or similar platforms.",
                "penalty": SEVERITY_PENALTIES["improve"]
            })
        
        return trust_score, issues
    
    def score_performance(self) -> Tuple[float, list]:
        """
        Score page performance using Google PageSpeed Insights.
        Returns (score, issues)
        """
        issues = []
        max_points = self.weights.get("performance", 10)
        
        if not self.pagespeed_data:
            # No PageSpeed data available
            return max_points * 0.5, [{
                "level": "info",
                "severity": "info",
                "title": "PageSpeed data unavailable",
                "detail": "Google PageSpeed Insights data could not be retrieved.",
                "penalty": 0
            }]
        
        score = self.pagespeed_data.get("score", 0)
        lcp = self.pagespeed_data.get("lcp", 0)
        fid = self.pagespeed_data.get("fid", 0)
        cls = self.pagespeed_data.get("cls", 0)
        
        # Score based on PageSpeed score (0-100)
        performance_score = (score / 100) * max_points
        
        # Add issues for poor metrics
        if lcp > 2.5:  # LCP > 2.5s is poor
            issues.append({
                "level": "high",
                "severity": "high",
                "title": f"Slow Largest Contentful Paint: {lcp:.1f}s",
                "detail": "LCP should be under 2.5s. Optimize images and server response time.",
                "penalty": SEVERITY_PENALTIES["high"]
            })
        
        if fid > 100:  # FID > 100ms is poor
            issues.append({
                "level": "high",
                "severity": "high",
                "title": f"High First Input Delay: {fid:.0f}ms",
                "detail": "FID should be under 100ms. Reduce JavaScript execution time.",
                "penalty": SEVERITY_PENALTIES["high"]
            })
        
        if cls > 0.1:  # CLS > 0.1 is poor
            issues.append({
                "level": "improve",
                "severity": "improve",
                "title": f"High Cumulative Layout Shift: {cls:.2f}",
                "detail": "CLS should be under 0.1. Add explicit width/height to images.",
                "penalty": SEVERITY_PENALTIES["improve"]
            })
        
        if score < 50:
            issues.append({
                "level": "critical",
                "severity": "critical",
                "title": f"Poor PageSpeed Score: {score}/100",
                "detail": "Page performance is critical for user experience and SEO.",
                "penalty": SEVERITY_PENALTIES["critical"]
            })
        
        return performance_score, issues
    
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
        max_points = self.weights.get("content_clarity", 20)
        
        base_score = max_points
        
        # Check meta description
        if not meta_desc:
            issues.append({
                "level": "critical",
                "severity": "critical",
                "title": "Missing meta description",
                "detail": "Add a compelling 120-155 character meta description for better CTR in search results.",
                "penalty": SEVERITY_PENALTIES["critical"]
            })
            base_score -= 5
        elif len(meta_desc) < 120 or len(meta_desc) > 155:
            issues.append({
                "level": "improve",
                "severity": "improve",
                "title": "Meta description length not optimal",
                "detail": f"Current: {len(meta_desc)} chars. Ideal: 120-155 characters.",
                "penalty": SEVERITY_PENALTIES["improve"]
            })
            base_score -= 2
        
        # Check for hierarchy
        if len(headings) < 2:
            issues.append({
                "level": "improve",
                "severity": "improve",
                "title": "Weak heading structure",
                "detail": "Use clear H2-H6 hierarchy to guide readers through content.",
                "penalty": SEVERITY_PENALTIES["improve"]
            })
            base_score -= 3
        
        # Check images
        total_images = len(images)
        if total_images > 0:
            images_without_alt = sum(1 for img in images if not img.get("has_alt"))
            if images_without_alt > 0:
                issues.append({
                    "level": "improve",
                    "severity": "improve",
                    "title": f"{images_without_alt}/{total_images} images missing alt text",
                    "detail": "Alt text improves accessibility and SEO. Add descriptive alt for every image.",
                    "penalty": SEVERITY_PENALTIES["improve"]
                })
                base_score -= 2
        
        return max(0, base_score), issues
    
    def calculate_score(self) -> Tuple[int, list]:
        """
        Calculate overall CRO score (0-100) with severity-based penalties.
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
        
        # Score performance if PageSpeed data available
        performance_score = 0
        performance_issues = []
        if self.pagespeed_data:
            performance_score, performance_issues = self.score_performance()
            all_issues.extend(performance_issues)
        
        # Store breakdown
        self.score_breakdown = {
            "cta": round(cta_score, 1),
            "headlines": round(headline_score, 1),
            "forms": round(form_score, 1),
            "trust_signals": round(trust_score, 1),
            "content_clarity": round(content_score, 1),
            "performance": round(performance_score, 1) if self.pagespeed_data else None
        }
        
        # Calculate total (sum of weighted scores)
        total_score = int(
            cta_score + 
            headline_score + 
            form_score + 
            trust_score + 
            content_score + 
            performance_score
        )
        
        # Apply severity penalties
        total_penalty = 0
        for issue in all_issues:
            total_penalty += issue.get("penalty", 0)
        
        # Final score with penalties
        final_score = max(0, min(100, total_score - total_penalty))
        
        # Add penalty info to response
        self.score_breakdown["penalty_total"] = total_penalty
        
        self.issues = all_issues
        
        return final_score, all_issues

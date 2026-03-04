"""GMB Scoring Engine with verifiable metrics only."""
from typing import Dict, Any, Tuple, List


class GMBScoringEngine:
    """
    Score GMB profile based on best practices.
    Only uses verifiable metrics - removed unverifiable customer response rate.
    
    Scoring Weights:
    - Profile Completeness: 30%
    - Reviews: 30%
    - Photos: 20%
    - Posts: 20%
    """
    
    WEIGHTS = {
        "profile_completeness": 30,
        "reviews": 30,
        "photos": 20,
        "posts": 20
    }
    
    def __init__(self, extracted_data: Dict[str, Any]):
        """Initialize with extracted GMB data."""
        self.data = extracted_data
        self.issues = []
        self.score_breakdown = {}
        self.data_source = extracted_data.get("data_source", "mock")
    
    def score_profile_completeness(self) -> Tuple[float, List[Dict]]:
        """
        Score profile completeness.
        Returns (score, issues)
        
        Checks: description, categories, hours, website, phone, photo, video
        """
        issues = []
        points = 0
        max_points = 30
        
        profile = self.data.get("profile_data", {})
        
        # Description (6 points)
        description = profile.get("description", "")
        if not description:
            issues.append({
                "level": "critical",
                "severity": "critical",
                "title": "Missing business description",
                "detail": "Add a compelling description (50-750 chars) explaining what you offer.",
                "penalty": 15
            })
        elif len(description) < 50:
            issues.append({
                "level": "improve",
                "severity": "improve",
                "title": "Description too short",
                "detail": f"Current: {len(description)} chars. Minimum 50 chars recommended.",
                "penalty": 5
            })
            points += 3
        else:
            points += 6
        
        # Categories (6 points)
        categories = profile.get("categories", [])
        if not categories:
            issues.append({
                "level": "critical",
                "severity": "critical",
                "title": "No categories selected",
                "detail": "Select relevant business categories to improve discoverability.",
                "penalty": 10
            })
        elif len(categories) < 2:
            issues.append({
                "level": "improve",
                "severity": "improve",
                "title": "Add more categories",
                "detail": "Add 2-3 relevant categories to reach more customers.",
                "penalty": 3
            })
            points += 4
        else:
            points += 6
        
        # Website (6 points)
        website = profile.get("website", "")
        if website:
            points += 6
        else:
            issues.append({
                "level": "improve",
                "severity": "improve",
                "title": "Missing website link",
                "detail": "Add a website URL for customers to visit your online presence.",
                "penalty": 5
            })
        
        # Phone (6 points)
        phone = profile.get("phone", "")
        if phone:
            points += 6
        else:
            issues.append({
                "level": "critical",
                "severity": "critical",
                "title": "Missing phone number",
                "detail": "Add your business phone number for customer inquiries.",
                "penalty": 10
            })
        
        # Hours (6 points)
        hours = profile.get("hours", {})
        if hours and len(hours) >= 5:  # At least 5 days
            points += 6
        else:
            issues.append({
                "level": "improve",
                "severity": "improve",
                "title": "Incomplete business hours",
                "detail": "Add complete operating hours for all days of the week.",
                "penalty": 3
            })
        
        # Total score
        score = (points / max_points) * 30
        return score, issues
    
    def score_reviews(self) -> Tuple[float, List[Dict]]:
        """
        Score review metrics (verifiable from SerpAPI).
        Returns (score, issues)
        
        Checks: total reviews, rating, recent activity
        """
        issues = []
        points = 0
        max_points = 30
        
        review_data = self.data.get("review_data", {})
        total_reviews = review_data.get("total_reviews", 0)
        rating = review_data.get("average_rating", 0)
        recent_reviews = review_data.get("reviews_last_30_days", 0)
        
        # Review count (12 points)
        if total_reviews >= 50:
            points += 12
        elif total_reviews >= 20:
            points += 8
            issues.append({
                "level": "improve",
                "severity": "improve",
                "title": "Low review count",
                "detail": f"Current: {total_reviews} reviews. Target: 50+ to establish credibility.",
                "penalty": 5
            })
        else:
            points += 4
            issues.append({
                "level": "critical",
                "severity": "critical",
                "title": "Very few reviews",
                "detail": f"Current: {total_reviews} reviews. Encourage customers to leave reviews.",
                "penalty": 10
            })
        
        # Rating (12 points)
        if rating >= 4.5:
            points += 12
        elif rating >= 4.0:
            points += 10
        elif rating >= 3.5:
            points += 6
            issues.append({
                "level": "improve",
                "severity": "improve",
                "title": "Rating below 4.0 stars",
                "detail": f"Current: {rating} stars. Focus on improving customer satisfaction.",
                "penalty": 5
            })
        else:
            points += 2
            issues.append({
                "level": "critical",
                "severity": "critical",
                "title": "Low average rating",
                "detail": f"Current: {rating} stars. Address customer concerns and improve service quality.",
                "penalty": 10
            })
        
        # Recent reviews (6 points)
        if recent_reviews >= 5:
            points += 6
        elif recent_reviews >= 2:
            points += 4
            issues.append({
                "level": "improve",
                "severity": "improve",
                "title": "Limited recent review activity",
                "detail": f"Current: {recent_reviews} reviews in last 30 days. Encourage recent customers to review.",
                "penalty": 3
            })
        else:
            issues.append({
                "level": "improve",
                "severity": "improve",
                "title": "No recent reviews",
                "detail": "No reviews in last 30 days. Encourage recent customers to leave reviews.",
                "penalty": 3
            })
        
        score = (points / max_points) * 30
        return score, issues
    
    def score_photos(self) -> Tuple[float, List[Dict]]:
        """
        Score photo metrics (verifiable from SerpAPI).
        Returns (score, issues)
        """
        issues = []
        points = 0
        max_points = 20
        
        metrics = self.data.get("content_metrics", {})
        photo_count = metrics.get("photo_count", 0)
        
        # Photo guidelines: 10+ is good, 30+ is excellent
        if photo_count >= 30:
            points = 20
        elif photo_count >= 15:
            points = 15
            issues.append({
                "level": "improve",
                "severity": "improve",
                "title": "Add more photos",
                "detail": f"Current: {photo_count} photos. Target: 30+ for better engagement.",
                "penalty": 3
            })
        elif photo_count >= 10:
            points = 12
            issues.append({
                "level": "improve",
                "severity": "improve",
                "title": "Limited photo library",
                "detail": f"Current: {photo_count} photos. Add interior, exterior, team, & product photos.",
                "penalty": 5
            })
        else:
            points = 6
            issues.append({
                "level": "critical",
                "severity": "critical",
                "title": f"Very few photos ({photo_count})",
                "detail": "Upload at least 10 photos showcasing your business, team, and services.",
                "penalty": 10
            })
        
        score = (points / max_points) * 20
        return score, issues
    
    def score_posts(self) -> Tuple[float, List[Dict]]:
        """
        Score post/content metrics.
        Returns (score, issues)
        """
        issues = []
        points = 0
        max_points = 20
        
        metrics = self.data.get("content_metrics", {})
        post_count = metrics.get("post_count", 0)
        recent_posts = metrics.get("posts_last_30_days", 0)
        
        # Recent posts are more important (12 points)
        if recent_posts >= 4:
            points += 12
        elif recent_posts >= 2:
            points += 8
            issues.append({
                "level": "improve",
                "severity": "improve",
                "title": "Inconsistent posting",
                "detail": "Post 1-2x per week to keep customers engaged and improve visibility.",
                "penalty": 5
            })
        else:
            points += 4
            issues.append({
                "level": "improve",
                "severity": "improve",
                "title": "No recent posts",
                "detail": f"No posts in last 30 days. Start posting regularly to boost SEO and engagement.",
                "penalty": 5
            })
        
        # Total post history (8 points)
        if post_count >= 30:
            points += 8
        elif post_count >= 15:
            points += 5
        
        score = (points / max_points) * 20
        return score, issues
    
    def calculate_score(self) -> Tuple[int, List[Dict], Dict[str, float]]:
        """
        Calculate overall GMB score (0-100).
        Returns (score, combined_issues, breakdown)
        """
        all_issues = []
        
        # Score each component
        completeness_score, completeness_issues = self.score_profile_completeness()
        all_issues.extend(completeness_issues)
        
        review_score, review_issues = self.score_reviews()
        all_issues.extend(review_issues)
        
        photo_score, photo_issues = self.score_photos()
        all_issues.extend(photo_issues)
        
        post_score, post_issues = self.score_posts()
        all_issues.extend(post_issues)
        
        # Store breakdown
        self.score_breakdown = {
            "profile_completeness": completeness_score,
            "reviews": review_score,
            "photos": photo_score,
            "posts": post_score,
            "data_source": self.data_source
        }
        
        # Calculate total
        total_score = int(
            completeness_score +
            review_score +
            photo_score +
            post_score
        )
        
        # Apply penalties
        total_penalty = 0
        for issue in all_issues:
            total_penalty += issue.get("penalty", 0)
        
        # Final score with penalties
        final_score = max(0, min(100, total_score - total_penalty))
        
        # Add penalty info
        self.score_breakdown["penalty_total"] = total_penalty
        
        self.issues = all_issues
        
        return final_score, all_issues, self.score_breakdown

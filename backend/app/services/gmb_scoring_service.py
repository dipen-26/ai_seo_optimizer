"""GMB Scoring Engine."""
from typing import Dict, Any, Tuple, List


class GMBScoringEngine:
    """
    Score GMB profile based on best practices.
    
    Scoring Weights:
    - Profile Completeness: 30%
    - Reviews: 25%
    - Photos: 15%
    - Posts: 15%
    - Engagement: 15%
    """
    
    WEIGHTS = {
        "profile_completeness": 30,
        "reviews": 25,
        "photos": 15,
        "posts": 15,
        "engagement": 15
    }
    
    def __init__(self, extracted_data: Dict[str, Any]):
        """Initialize with extracted GMB data."""
        self.data = extracted_data
        self.issues = []
        self.score_breakdown = {}
    
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
        
        # Description (5 points)
        description = profile.get("description", "")
        if not description:
            issues.append({
                "level": "critical",
                "title": "Missing business description",
                "detail": "Add a compelling description (50-750 chars) explaining what you offer."
            })
        elif len(description) < 50:
            issues.append({
                "level": "improve",
                "title": "Description too short",
                "detail": f"Current: {len(description)} chars. Minimum 50 chars recommended."
            })
            points += 2
        else:
            points += 5
        
        # Categories (5 points)
        categories = profile.get("categories", [])
        if not categories:
            issues.append({
                "level": "critical",
                "title": "No categories selected",
                "detail": "Select relevant business categories to improve discoverability."
            })
        elif len(categories) < 2:
            issues.append({
                "level": "improve",
                "title": "Add more categories",
                "detail": "Add 2-3 relevant categories to reach more customers."
            })
            points += 3
        else:
            points += 5
        
        # Website (5 points)
        website = profile.get("website", "")
        if website:
            points += 5
        else:
            issues.append({
                "level": "improve",
                "title": "Missing website link",
                "detail": "Add a website URL for customers to visit your online presence."
            })
        
        # Phone (5 points)
        phone = profile.get("phone", "")
        if phone:
            points += 5
        else:
            issues.append({
                "level": "critical",
                "title": "Missing phone number",
                "detail": "Add your business phone number for customer inquiries."
            })
        
        # Hours (5 points)
        hours = profile.get("hours", {})
        if hours and len(hours) >= 5:  # At least 5 days
            points += 5
        else:
            issues.append({
                "level": "improve",
                "title": "Incomplete business hours",
                "detail": "Add complete operating hours for all days of the week."
            })
        
        # Total score
        score = (points / max_points) * 30  # Convert to weight percentage
        return score, issues
    
    def score_reviews(self) -> Tuple[float, List[Dict]]:
        """
        Score review metrics.
        Returns (score, issues)
        
        Checks: total reviews, rating, recent activity
        """
        issues = []
        points = 0
        max_points = 25
        
        review_data = self.data.get("review_data", {})
        total_reviews = review_data.get("total_reviews", 0)
        rating = review_data.get("average_rating", 0)
        recent_reviews = review_data.get("reviews_last_30_days", 0)
        
        # Review count (10 points)
        if total_reviews >= 50:
            points += 10
        elif total_reviews >= 20:
            points += 7
            issues.append({
                "level": "improve",
                "title": "Low review count",
                "detail": f"Current: {total_reviews} reviews. Target: 50+ to establish credibility."
            })
        else:
            points += 3
            issues.append({
                "level": "critical",
                "title": "Very few reviews",
                "detail": f"Current: {total_reviews} reviews. Encourage customers to leave reviews."
            })
        
        # Rating (10 points)
        if rating >= 4.5:
            points += 10
        elif rating >= 4.0:
            points += 8
        elif rating >= 3.5:
            points += 5
            issues.append({
                "level": "improve",
                "title": "Rating below 4.0 stars",
                "detail": f"Current: {rating}⭐. Focus on improving customer satisfaction."
            })
        else:
            points += 2
            issues.append({
                "level": "critical",
                "title": "Low average rating",
                "detail": f"Current: {rating}⭐. Address customer concerns and improve service quality."
            })
        
        # Recent reviews (5 points)
        if recent_reviews >= 5:
            points += 5
        elif recent_reviews >= 2:
            points += 3
        else:
            issues.append({
                "level": "improve",
                "title": "Limited recent review activity",
                "detail": f"No reviews in last 30 days. Encourage recent customers to review."
            })
        
        score = (points / max_points) * 25
        return score, issues
    
    def score_photos(self) -> Tuple[float, List[Dict]]:
        """
        Score photo metrics.
        Returns (score, issues)
        """
        issues = []
        points = 0
        max_points = 15
        
        metrics = self.data.get("content_metrics", {})
        photo_count = metrics.get("photo_count", 0)
        
        # Photo guidelines: 10+ is good, 30+ is excellent
        if photo_count >= 30:
            points = 15
        elif photo_count >= 15:
            points = 12
            issues.append({
                "level": "improve",
                "title": "Add more photos",
                "detail": f"Current: {photo_count} photos. Target: 30+ for better engagement."
            })
        elif photo_count >= 10:
            points = 10
            issues.append({
                "level": "improve",
                "title": "Limited photo library",
                "detail": f"Current: {photo_count} photos. Add interior, exterior, team, & product photos."
            })
        else:
            points = 5
            issues.append({
                "level": "critical",
                "title": f"Very few photos ({photo_count})",
                "detail": "Upload at least 10 photos showcasing your business, team, and services."
            })
        
        score = (points / max_points) * 15
        return score, issues
    
    def score_posts(self) -> Tuple[float, List[Dict]]:
        """
        Score post/content metrics.
        Returns (score, issues)
        """
        issues = []
        points = 0
        max_points = 15
        
        metrics = self.data.get("content_metrics", {})
        post_count = metrics.get("post_count", 0)
        recent_posts = metrics.get("posts_last_30_days", 0)
        
        # Recent posts are more important
        if recent_posts >= 4:
            points += 10
        elif recent_posts >= 2:
            points += 7
            issues.append({
                "level": "improve",
                "title": "Inconsistent posting",
                "detail": "Post 1-2x per week to keep customers engaged and improve visibility."
            })
        else:
            points += 3
            issues.append({
                "level": "improve",
                "title": "No recent posts",
                "detail": f"No posts in last 30 days. Start posting regularly to boost SEO and engagement."
            })
        
        # Total post history
        if post_count >= 30:
            points += 5
        elif post_count >= 15:
            points += 3
        
        score = (points / max_points) * 15
        return score, issues
    
    def score_engagement(self) -> Tuple[float, List[Dict]]:
        """
        Score engagement metrics.
        Returns (score, issues)
        """
        issues = []
        points = 0
        max_points = 15
        
        engagement = self.data.get("engagement_metrics", {})
        response_rate = engagement.get("customer_responses_rate", 0)
        monetization = engagement.get("monetization_enabled", False)
        
        # Customer response rate
        if response_rate >= 80:
            points += 10
        elif response_rate >= 50:
            points += 7
        elif response_rate > 0:
            points += 4
            issues.append({
                "level": "improve",
                "title": "Low customer response rate",
                "detail": f"Current: {response_rate}%. Respond to reviews and messages promptly."
            })
        else:
            points += 1
            issues.append({
                "level": "critical",
                "title": "No customer engagement",
                "detail": "Respond to reviews and messages to build customer relationships."
            })
        
        # Monetization (Google services like ordering, bookings)
        if monetization:
            points += 5
        else:
            issues.append({
                "level": "improve",
                "title": "Enable monetization features",
                "detail": "Enable Google booking, ordering, or message features to increase conversions."
            })
        
        score = (points / max_points) * 15
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
        
        engagement_score, engagement_issues = self.score_engagement()
        all_issues.extend(engagement_issues)
        
        # Store breakdown
        self.score_breakdown = {
            "profile_completeness": completeness_score,
            "reviews": review_score,
            "photos": photo_score,
            "posts": post_score,
            "engagement": engagement_score
        }
        
        # Calculate total
        total_score = int(
            completeness_score +
            review_score +
            photo_score +
            post_score +
            engagement_score
        )
        
        # Limit to 100
        total_score = min(100, max(0, total_score))
        
        self.issues = all_issues
        
        return total_score, all_issues, self.score_breakdown

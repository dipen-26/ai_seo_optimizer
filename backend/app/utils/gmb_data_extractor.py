"""GMB Data Extractor - Extract or mock GMB profile data."""
from typing import Dict, Any, Optional, List
import random


class GMBDataExtractor:
    """
    Extract GMB profile data.
    
    Phase 1: Mock realistic data
    Phase 2: Integrate with Google Maps API or scraping
    """
    
    def __init__(self, business_name: str, location: Optional[str] = None):
        """
        Initialize with business information.
        
        Args:
            business_name: Name of the business
            location: Optional location/address
        """
        self.business_name = business_name
        self.location = location or "Location not specified"
    
    def extract_mock_data(self) -> Dict[str, Any]:
        """
        Extract/Generate mock GMB profile data.
        
        Returns:
            Dictionary with GMB profile metrics
        """
        # Generate realistic mock data based on business name characteristics
        base_rating = round(random.uniform(3.5, 4.9), 1)
        review_count = random.randint(10, 500)
        photo_count = random.randint(5, 120)
        post_count = random.randint(0, 50)
        
        # Engagement based on post frequency
        months_active = random.randint(3, 36)
        avg_monthly_posts = post_count / max(months_active, 1)
        
        return {
            "business_name": self.business_name,
            "location": self.location,
            "profile_data": {
                "rating": base_rating,
                "review_count": review_count,
                "categories": ["Restaurant", "Service Business"],
                "description": f"Professional {self.business_name} serving {self.location}",
                "phone": "+1 (555) 000-0000",
                "website": "",
                "hours": {
                    "Monday": "9:00 AM - 5:00 PM",
                    "Tuesday": "9:00 AM - 5:00 PM",
                    "Wednesday": "9:00 AM - 5:00 PM",
                    "Thursday": "9:00 AM - 5:00 PM",
                    "Friday": "9:00 AM - 5:00 PM",
                    "Saturday": "10:00 AM - 3:00 PM",
                    "Sunday": "Closed"
                }
            },
            "content_metrics": {
                "photo_count": photo_count,
                "video_count": random.randint(0, 10),
                "post_count": post_count,
                "posts_last_30_days": random.randint(0, min(5, post_count)),
            },
            "engagement_metrics": {
                "avg_monthly_posts": round(avg_monthly_posts, 2),
                "customer_responses_rate": round(random.uniform(0, 100), 1),
                "monetization_enabled": random.choice([True, False])
            },
            "review_data": {
                "total_reviews": review_count,
                "reviews_last_30_days": random.randint(0, max(5, review_count // 10)),
                "average_rating": base_rating,
                "rating_distribution": {
                    "5_stars": random.randint(int(review_count * 0.5), review_count),
                    "4_stars": random.randint(0, int(review_count * 0.3)),
                    "3_stars": random.randint(0, int(review_count * 0.15)),
                    "2_stars": random.randint(0, int(review_count * 0.05)),
                    "1_star": random.randint(0, int(review_count * 0.05))
                }
            }
        }
    
    def extract_all(self) -> Dict[str, Any]:
        """Extract all GMB data."""
        return self.extract_mock_data()

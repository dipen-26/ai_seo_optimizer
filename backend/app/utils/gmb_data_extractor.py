"""GMB Data Extractor - Free scraping only, no paid APIs."""
from typing import Dict, Any, Optional, List
import random
import re
import httpx
import asyncio
from ..core.config import SERPAPI_KEY, HTTP_TIMEOUT


class GMBDataExtractor:
    """
    Extract GMB profile data using free scraping methods.
    Priority: Google Search → Alternative Sources → Mock
    """
    
    def __init__(self, business_name: str, location: Optional[str] = None):
        self.business_name = business_name
        self.location = location or ""
        self.serpapi_key = SERPAPI_KEY
    
    async def extract_all(self) -> Dict[str, Any]:
        """Extract GMB data using free scraping methods."""
        
        # Strategy 1: Try Google Search with mobile user agent
        google_data = await self._fetch_from_google_mobile()
        if google_data and google_data.get("rating", 0) > 0:
            return google_data
        
        # Strategy 2: Try alternative - scrape from business directory sites
        directory_data = await self._fetch_from_directories()
        if directory_data and directory_data.get("rating", 0) > 0:
            return directory_data
        
        # Strategy 3: Try with different approach - use textise dot iitty
        textise_data = await self._fetch_from_textise()
        if textise_data and textise_data.get("rating", 0) > 0:
            return textise_data
        
        # Fallback: Smart mock based on business type
        return self._generate_smart_mock_data()
    
    async def _fetch_from_google_mobile(self) -> Optional[Dict[str, Any]]:
        """Fetch from Google using mobile user agent."""
        try:
            search_query = f"{self.business_name} {self.location}".strip()
            
            # Use mobile user agent
            headers = {
                "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.0 Mobile/15E148 Safari/604.1",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                "Accept-Language": "en-US,en;q=0.5",
                "Accept-Encoding": "gzip, deflate",
                "Connection": "keep-alive",
            }
            
            async with httpx.AsyncClient(timeout=20, follow_redirects=True) as client:
                url = f"https://www.google.com/search?q={search_query.replace(' ', '+')}&hl=en"
                response = await client.get(url, headers=headers)
                
                if response.status_code == 200:
                    result = self._parse_google_mobile_results(response.text)
                    if result:
                        return result
                        
        except Exception as e:
            print(f"Google Mobile error: {e}")
        
        return None
    
    def _parse_google_mobile_results(self, html: str) -> Optional[Dict[str, Any]]:
        """Parse Google mobile search results."""
        
        # Check if we got a CAPTCHA or block page
        if "captcha" in html.lower() or "unusual traffic" in html.lower():
            print("Google blocking - CAPTCHA or traffic block detected")
            return None
        
        rating = 0
        reviews = 0
        
        # More patterns for mobile results
        patterns = [
            # Standard patterns
            r'(\\d+\\.?\\d*)\\s*(?:stars?|★)',
            r'(\\d+\\.?\\d*)\\s*/\\s*5',
            # Review count
            r'(\\d+[,\\d]*)\\s*reviews?',
            r'\\(\\s*(\\d+[,\\d]*)\\s*reviews?\\s*\\)',
        ]
        
        # Try to find rating
        for pattern in patterns[:2]:
            match = re.search(pattern, html, re.IGNORECASE)
            if match:
                rating = float(match.group(1))
                if rating <= 5:
                    break
        
        # Try to find reviews
        for pattern in patterns[2:]:
            match = re.search(pattern, html, re.IGNORECASE)
            if match:
                reviews = int(match.group(1).replace(',', ''))
                break
        
        # Look for business info in structured data
        if 'application/ld+json' in html:
            try:
                json_matches = re.findall(r'<script[^>]*type="application/ld\+json"[^>]*>(.*?)</script>', html, re.DOTALL)
                for json_str in json_matches:
                    if '"@type"' in json_str and '"aggregateRating"' in json_str:
                        import json
                        data = json.loads(json_str)
                        if isinstance(data, dict):
                            rating = rating or float(data.get("aggregateRating", {}).get("ratingValue", 0))
                            reviews = reviews or int(data.get("aggregateRating", {}).get("reviewCount", 0))
            except:
                pass
        
        if rating > 0:
            return self._build_result(rating, reviews, "google_mobile")
        
        return None
    
    async def _fetch_from_directories(self) -> Optional[Dict[str, Any]]:
        """Try scraping from business directory sites."""
        try:
            search_query = f"{self.business_name} {self.location}".strip()
            
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            }
            
            async with httpx.AsyncClient(timeout=15, follow_redirects=True) as client:
                # Try Yelp
                try:
                    yelp_query = search_query.replace(' ', '-').lower()
                    response = await client.get(f"https://www.yelp.com/search?find_desc={yelp_query}&find_loc={self.location}", headers=headers)
                    if response.status_code == 200:
                        result = self._parse_yelp_results(response.text)
                        if result:
                            return result
                except:
                    pass
                
                # Try YellowPages
                try:
                    response = await client.get(f"https://www.yellowpages.com/search?search_terms={search_query}", headers=headers)
                    if response.status_code == 200:
                        result = self._parse_yellowpages(response.text)
                        if result:
                            return result
                except:
                    pass
                    
        except Exception as e:
            print(f"Directory error: {e}")
        
        return None
    
    def _parse_yelp_results(self, html: str) -> Optional[Dict[str, Any]]:
        """Parse Yelp search results."""
        rating = 0
        reviews = 0
        
        # Yelp rating pattern: data-star-rating="4.5" or i-stars class
        rating_match = re.search(r'i-stars[^>]*title="([^"]+)"', html)
        if rating_match:
            rating_match = re.search(r'(\d+\.?\d*)', rating_match.group(1))
            if rating_match:
                rating = float(rating_match.group(1))
        
        # Review count
        review_match = re.search(r'(\d+)\s*reviews?', html, re.IGNORECASE)
        if review_match:
            reviews = int(review_match.group(1))
        
        if rating > 0:
            return self._build_result(rating, reviews, "yelp")
        
        return None
    
    def _parse_yellowpages(self, html: str) -> Optional[Dict[str, Any]]:
        """Parse YellowPages results."""
        rating = 0
        reviews = 0
        
        rating_match = re.search(r'ratingValue[^>]*"(\d+\.?\d*)"', html)
        if rating_match:
            rating = float(rating_match.group(1))
        
        review_match = re.search(r'reviewCount[^>]*"(\d+)"', html)
        if review_match:
            reviews = int(review_match.group(1))
        
        if rating > 0:
            return self._build_result(rating, reviews, "yellowpages")
        
        return None
    
    async def _fetch_from_textise(self) -> Optional[Dict[str, Any]]:
        """Try textise dot iitty alternative."""
        try:
            search_query = f"{self.business_name} {self.location}".strip()
            
            headers = {
                "User-Agent": "Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)",
            }
            
            async with httpx.AsyncClient(timeout=15, follow_redirects=True) as client:
                # Try textise dot iitty
                url = f"https://www.textise dot iitty.com/search?q={search_query.replace(' ', '+')}"
                # This is a placeholder - in reality these services come and go
                    
        except Exception as e:
            print(f"Textise error: {e}")
        
        return None
    
    def _build_result(self, rating: float, reviews: int, source: str) -> Dict[str, Any]:
        """Build standardized result dict."""
        return {
            "business_name": self.business_name,
            "location": self.location,
            "profile_data": {
                "rating": rating,
                "review_count": reviews,
                "categories": self._detect_categories(),
                "description": "",
                "phone": "",
                "website": "",
                "address": self.location,
                "hours": {}
            },
            "content_metrics": {
                "photo_count": 5,
                "video_count": 0,
                "post_count": 0,
                "posts_last_30_days": 0,
            },
            "engagement_metrics": {
                "avg_monthly_posts": 0,
                "customer_responses_rate": 0,
                "monetization_enabled": False
            },
            "review_data": {
                "total_reviews": reviews,
                "reviews_last_30_days": 0,
                "average_rating": rating,
                "rating_distribution": self._estimate_rating_distribution(reviews)
            },
            "data_source": source,
            "data_note": f"Data scraped from {source}"
        }
    
    def _estimate_rating_distribution(self, total_reviews: int) -> Dict[str, int]:
        if total_reviews == 0:
            return {"5_stars": 0, "4_stars": 0, "3_stars": 0, "2_stars": 0, "1_star": 0}
        
        return {
            "5_stars": int(total_reviews * 0.6),
            "4_stars": int(total_reviews * 0.2),
            "3_stars": int(total_reviews * 0.1),
            "2_stars": int(total_reviews * 0.05),
            "1_star": int(total_reviews * 0.05)
        }
    
    def _generate_smart_mock_data(self) -> Dict[str, Any]:
        """Generate smart mock data based on business type with realistic values."""
        name_hash = hash(self.business_name.lower().replace(" ", ""))
        random.seed(name_hash)
        
        # Generate realistic values based on business type
        categories = self._detect_categories()
        
        # Different rating ranges based on business type
        if any(cat in ["Restaurant", "Food & Drink"] for cat in categories):
            base_rating = round(random.uniform(3.8, 4.7), 1)
            review_count = random.randint(50, 500)
            photo_count = random.randint(10, 50)
        elif any(cat in ["Medical", "Health"] for cat in categories):
            base_rating = round(random.uniform(4.0, 4.9), 1)
            review_count = random.randint(20, 200)
            photo_count = random.randint(5, 20)
        elif any(cat in ["Salon", "Beauty"] for cat in categories):
            base_rating = round(random.uniform(3.5, 4.8), 1)
            review_count = random.randint(30, 150)
            photo_count = random.randint(15, 40)
        else:
            base_rating = round(random.uniform(3.5, 4.5), 1)
            review_count = random.randint(10, 100)
            photo_count = random.randint(5, 25)
        
        return {
            "business_name": self.business_name,
            "location": self.location or "Location not specified",
            "profile_data": {
                "rating": base_rating,
                "review_count": review_count,
                "categories": categories,
                "description": f"Professional {self.business_name} services in {self.location or 'your area'}",
                "phone": "",
                "website": "",
                "address": self.location,
                "hours": {}
            },
            "content_metrics": {
                "photo_count": photo_count,
                "video_count": random.randint(0, 3),
                "post_count": random.randint(0, 10),
                "posts_last_30_days": random.randint(0, 3),
            },
            "engagement_metrics": {
                "avg_monthly_posts": random.randint(0, 4),
                "customer_responses_rate": round(random.uniform(0.1, 0.5), 2),
                "monetization_enabled": random.choice([True, False])
            },
            "review_data": {
                "total_reviews": review_count,
                "reviews_last_30_days": random.randint(0, 20),
                "average_rating": base_rating,
                "rating_distribution": self._estimate_rating_distribution(review_count)
            },
            "data_source": "estimated",
            "data_note": "Estimated data based on business type - search engines blocked automated requests"
        }
    
    def _detect_categories(self) -> List[str]:
        name_lower = self.business_name.lower()
        
        if any(p in name_lower for p in ["restaurant", "cafe", "coffee", "pizza", "food", "starbucks", "mcdonald", "burger", "grill", "diner"]):
            return ["Restaurant", "Food & Drink"]
        elif any(p in name_lower for p in ["clinic", "medical", "health", "dental", "hospital", "doctor", "physician"]):
            return ["Medical", "Health"]
        elif any(p in name_lower for p in ["outfit", "clothing", "fashion", "boutique", "store", "shop", "retail"]):
            return ["Clothing Store", "Fashion"]
        elif any(p in name_lower for p in ["hotel", "inn", "suites", "motel", "resort"]):
            return ["Hotel", "Accommodation"]
        elif any(p in name_lower for p in ["gym", "fitness", "health club", "workout", "crossfit"]):
            return ["Gym", "Fitness"]
        elif any(p in name_lower for p in ["salon", "spa", "beauty", "hair", "nail", "barber"]):
            return ["Salon", "Beauty"]
        elif any(p in name_lower for p in ["auto", "car", "vehicle", "repair", "mechanic", "tire", "oil"]):
            return ["Auto Repair", "Automotive"]
        elif any(p in name_lower for p in ["plumber", "electric", "hvac", "roofing", "construction", "contractor"]):
            return ["Home Services", "Contractor"]
        elif any(p in name_lower for p in ["lawyer", "attorney", "legal", "law"]):
            return ["Legal", "Lawyer"]
        elif any(p in name_lower for p in ["real estate", "realtor", "property", "realty"]):
            return ["Real Estate", "Property"]
        else:
            return ["Business"]
    
    def extract_mock_data(self) -> Dict[str, Any]:
        return self._generate_smart_mock_data()

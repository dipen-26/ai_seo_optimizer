"""Data extractor for CRO analysis with advanced detection."""
from typing import Dict, List, Any, Optional
from bs4 import BeautifulSoup
import json
import re


class CRODataExtractor:
    """Extract CRO-relevant data from parsed HTML."""
    
    def __init__(self, soup: BeautifulSoup, page_data: Optional[Dict[str, Any]] = None):
        """Initialize with BeautifulSoup object."""
        self.soup = soup
        self.page_data = page_data or {}
        self.html = self.page_data.get("html", "")
    
    def extract_title(self) -> Optional[str]:
        """Extract page title."""
        title_tag = self.soup.find("title")
        if title_tag:
            return title_tag.get_text(strip=True)
        return None
    
    def extract_meta_description(self) -> Optional[str]:
        """Extract meta description."""
        meta_desc = self.soup.find("meta", attrs={"name": "description"})
        if meta_desc and meta_desc.get("content"):
            return meta_desc.get("content")
        return None
    
    def extract_h1_tags(self) -> List[str]:
        """Extract all H1 tags."""
        h1_tags = self.soup.find_all("h1")
        return [tag.get_text(strip=True) for tag in h1_tags if tag.get_text(strip=True)]
    
    def extract_headings(self) -> Dict[str, List[str]]:
        """Extract all heading tags."""
        headings = {}
        for level in range(2, 7):  # H2-H6
            tag_name = f"h{level}"
            tags = self.soup.find_all(tag_name)
            if tags:
                headings[tag_name] = [tag.get_text(strip=True) for tag in tags if tag.get_text(strip=True)]
        return headings
    
    def extract_meta_keywords(self) -> Optional[str]:
        """Extract meta keywords."""
        meta_keywords = self.soup.find("meta", attrs={"name": "keywords"})
        if meta_keywords and meta_keywords.get("content"):
            return meta_keywords.get("content")
        return None
    
    def extract_buttons(self) -> List[Dict[str, str]]:
        """
        Extract all button elements including:
        - <button> tags
        - <a> with button classes
        - <input type="submit">
        - <input type="button">
        - Elements with role="button"
        """
        buttons = []
        
        # 1. <button> tags
        button_tags = self.soup.find_all("button")
        for btn in button_tags:
            text = btn.get_text(strip=True)
            classes = " ".join(btn.get("class", []))
            buttons.append({
                "type": "button",
                "text": text,
                "classes": classes,
                "tag": "button"
            })
        
        # 2. <a> with button-like classes
        a_buttons = self.soup.find_all("a", class_=lambda x: x and any(
            c in x.lower() for c in ["btn", "button", "cta", "call-to-action", "primary", "action"]
        ))
        for link in a_buttons:
            text = link.get_text(strip=True)
            if text:
                buttons.append({
                    "type": "link",
                    "text": text,
                    "href": link.get("href", "#"),
                    "classes": " ".join(link.get("class", [])),
                    "tag": "a"
                })
        
        # 3. Input submit/button elements
        input_submits = self.soup.find_all("input", {"type": ["submit", "button"]})
        for inp in input_submits:
            value = inp.get("value", "") or "Submit"
            classes = " ".join(inp.get("class", []))
            buttons.append({
                "type": "input_submit",
                "text": value,
                "classes": classes,
                "tag": "input"
            })
        
        # 4. Elements with role="button"
        aria_buttons = self.soup.find_all(attrs={"role": "button"})
        for btn in aria_buttons:
            text = btn.get_text(strip=True)
            if text:
                classes = " ".join(btn.get("class", []))
                buttons.append({
                    "type": "role_button",
                    "text": text,
                    "classes": classes,
                    "tag": btn.name or "div"
                })
        
        # 5. Check for divs styled as buttons (common patterns)
        divs = self.soup.find_all("div")
        for div in divs:
            classes = " ".join(div.get("class", [])).lower()
            # Check for common button class patterns
            if any(c in classes for c in ["btn", "button", "cta", "primary-", "submit-"]):
                text = div.get_text(strip=True)
                if text and len(text) < 50:  # Button text should be short
                    buttons.append({
                        "type": "div_button",
                        "text": text,
                        "classes": " ".join(div.get("class", [])),
                        "tag": "div"
                    })
        
        return buttons
    
    def extract_forms(self) -> List[Dict[str, Any]]:
        """Extract form information."""
        forms = []
        form_tags = self.soup.find_all("form")
        
        for idx, form in enumerate(form_tags):
            form_data = {
                "index": idx,
                "action": form.get("action", ""),
                "method": form.get("method", "POST").upper(),
                "fields": []
            }
            
            # Find all input fields
            inputs = form.find_all(["input", "textarea", "select"])
            for inp in inputs:
                field_type = inp.get("type", "text")
                field_name = inp.get("name", f"field_{len(form_data['fields'])}")
                field_placeholder = inp.get("placeholder", "")
                
                form_data["fields"].append({
                    "type": field_type,
                    "name": field_name,
                    "placeholder": field_placeholder,
                    "required": inp.has_attr("required")
                })
            
            forms.append(form_data)
        
        return forms
    
    def extract_images(self) -> List[Dict[str, str]]:
        """Extract image information."""
        images = []
        img_tags = self.soup.find_all("img")
        
        for img in img_tags:
            src = img.get("src", "")
            alt = img.get("alt", "")
            images.append({
                "src": src,
                "alt": alt,
                "has_alt": bool(alt)
            })
        
        return images
    
    def extract_schema_markup(self) -> Dict[str, Any]:
        """
        Extract structured data (JSON-LD schema.org markup).
        
        Returns:
            Dictionary with found schema types and data
        """
        schema_data = {
            "has_schema": False,
            "schema_types": [],
            "review_schemas": [],
            "rating_schemas": [],
            "trust_signals": {
                "has_review_schema": False,
                "has_aggregate_rating": False,
                "has_product_schema": False,
                "has_organization_schema": False,
                "has_local_business_schema": False
            }
        }
        
        # Find all JSON-LD scripts
        json_ld_scripts = self.soup.find_all("script", type="application/ld+json")
        
        for script in json_ld_scripts:
            try:
                # Handle both single object and array of objects
                content = script.string
                if not content:
                    continue
                    
                data = json.loads(content)
                
                # Normalize to list
                if isinstance(data, dict):
                    data = [data]
                
                for item in data:
                    # Extract @type
                    schema_type = item.get("@type", "")
                    if schema_type:
                        schema_data["has_schema"] = True
                        schema_data["schema_types"].append(schema_type)
                        
                        # Check for specific trust-related schemas
                        if isinstance(schema_type, list):
                            schema_type = " ".join(schema_type)
                        
                        schema_type_lower = str(schema_type).lower()
                        
                        # Review/Rating schemas
                        if "review" in schema_type_lower:
                            schema_data["trust_signals"]["has_review_schema"] = True
                            schema_data["review_schemas"].append(item)
                            
                            # Check for rating
                            if item.get("reviewRating"):
                                schema_data["trust_signals"]["has_aggregate_rating"] = True
                                schema_data["rating_schemas"].append(item.get("reviewRating"))
                        
                        if "aggregaterating" in schema_type_lower:
                            schema_data["trust_signals"]["has_aggregate_rating"] = True
                            rating = item.get("ratingValue") or item.get("bestRating")
                            if rating:
                                schema_data["rating_schemas"].append(item)
                        
                        # Organization schema
                        if "organization" in schema_type_lower:
                            schema_data["trust_signals"]["has_organization_schema"] = True
                        
                        # Local business schema
                        if "localbusiness" in schema_type_lower or "physicalstore" in schema_type_lower:
                            schema_data["trust_signals"]["has_local_business_schema"] = True
                        
                        # Product schema
                        if "product" in schema_type_lower:
                            schema_data["trust_signals"]["has_product_schema"] = True
                            
            except (json.JSONDecodeError, AttributeError):
                continue
        
        return schema_data
    
    def extract_trust_signals(self) -> Dict[str, Any]:
        """
        Extract comprehensive trust signals:
        - Schema.org markup (JSON-LD)
        - SSL/HTTPS indicator
        - Third-party trust badges
        - Security certifications
        """
        signals = {
            "is_https": self.page_data.get("is_https", False),
            "has_ssl": self.page_data.get("is_https", False),
            "schema": self.extract_schema_markup(),
            "third_party_reviews": [],
            "security_badges": [],
            "certifications": []
        }
        
        # Check for third-party review embeds
        html_lower = self.html.lower()
        
        # Trust review platforms
        review_platforms = [
            "trustpilot", "g2", "capterra", "getapp", "softwareadvice",
            "yelp", "bbb.org", "glassdoor", "sitejabber", "resellerRatings"
        ]
        
        for platform in review_platforms:
            if platform in html_lower:
                signals["third_party_reviews"].append(platform)
        
        # Security badges/logos
        security_patterns = [
            "norton", "mcafee", "ssl", "tls", "https", "secure",
            "privacy", "trust", "verified", "securecheckout", "encrypted"
        ]
        
        for pattern in security_patterns:
            if pattern in html_lower:
                signals["security_badges"].append(pattern)
        
        # Check for certification logos
        cert_patterns = [
            "iso", "certified", "badge", "member", "accredited",
            "Better Business Bureau", "BBB", "chamber"
        ]
        
        for pattern in cert_patterns:
            if pattern in html_lower:
                signals["certifications"].append(pattern)
        
        # Calculate overall trust score
        trust_score = 0
        
        if signals["is_https"]:
            trust_score += 2
        if signals["schema"]["has_schema"]:
            trust_score += 3
            if signals["schema"]["trust_signals"]["has_aggregate_rating"]:
                trust_score += 2
            if signals["schema"]["trust_signals"]["has_review_schema"]:
                trust_score += 2
        if signals["third_party_reviews"]:
            trust_score += 2
        if signals["security_badges"]:
            trust_score += 1
        
        signals["trust_score"] = min(trust_score, 10)  # Max 10 points
        
        return signals
    
    def extract_cta_positions(self) -> Dict[str, Any]:
        """
        Extract CTA position information from page data.
        
        Returns:
            Dictionary with CTA positioning info
        """
        # This will be enriched by viewport_detector
        viewport_data = self.page_data.get("viewport", {})
        
        return {
            "viewport_width": viewport_data.get("width", 1280),
            "viewport_height": viewport_data.get("height", 720),
            "is_js_rendered": self.page_data.get("js_rendered", False)
        }
    
    def extract_all(self) -> Dict[str, Any]:
        """Extract all CRO-relevant data."""
        return {
            "title": self.extract_title(),
            "meta_description": self.extract_meta_description(),
            "meta_keywords": self.extract_meta_keywords(),
            "h1_tags": self.extract_h1_tags(),
            "headings": self.extract_headings(),
            "buttons": self.extract_buttons(),
            "forms": self.extract_forms(),
            "images": self.extract_images(),
            "trust_signals": self.extract_trust_signals(),
            "schema": self.extract_schema_markup(),
            "cta_positions": self.extract_cta_positions()
        }

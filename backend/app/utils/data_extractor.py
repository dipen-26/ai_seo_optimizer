"""Data extractor for CRO analysis."""
from typing import Dict, List, Any, Optional
from bs4 import BeautifulSoup


class CRODataExtractor:
    """Extract CRO-relevant data from parsed HTML."""
    
    def __init__(self, soup: BeautifulSoup):
        """Initialize with BeautifulSoup object."""
        self.soup = soup
    
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
        """Extract button elements and their text."""
        buttons = []
        button_tags = self.soup.find_all("button")
        a_buttons = self.soup.find_all("a", class_=lambda x: x and ("btn" in x or "button" in x))
        
        for btn in button_tags:
            text = btn.get_text(strip=True)
            if text:
                buttons.append({
                    "type": "button",
                    "text": text,
                    "classes": " ".join(btn.get("class", []))
                })
        
        for link in a_buttons:
            text = link.get_text(strip=True)
            if text:
                buttons.append({
                    "type": "link",
                    "text": text,
                    "href": link.get("href", "#"),
                    "classes": " ".join(link.get("class", []))
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
            "images": self.extract_images()
        }

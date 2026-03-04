"""Configuration module for AI SEO Optimizer."""
import os
from dotenv import load_dotenv

load_dotenv()

# API Configuration
API_TITLE = "AI SEO Optimizer"
API_VERSION = "0.2.0"

# AI Service Configuration
# Priority: OpenRouter (free) > OpenAI (paid)
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")

# Use OpenRouter if available, fallback to OpenAI
if OPENROUTER_API_KEY:
    AI_API_KEY = OPENROUTER_API_KEY
    AI_BASE_URL = os.getenv("AI_BASE_URL", "https://openrouter.ai/api/v1")
    # Default to best free model
    AI_MODEL = os.getenv("AI_MODEL", "deepseek/deepseek-chat")
    USE_OPENROUTER = True
else:
    AI_API_KEY = OPENAI_API_KEY
    AI_BASE_URL = os.getenv("AI_BASE_URL", "https://api.openai.com/v1")
    AI_MODEL = os.getenv("AI_MODEL", "gpt-4")
    USE_OPENROUTER = False

# Timeout Configuration
HTTP_TIMEOUT = 30
SCRAPE_TIMEOUT = 45

# Playwright Configuration
PLAYWRIGHT_TIMEOUT = int(os.getenv("PLAYWRIGHT_TIMEOUT", "45000"))
PLAYWRIGHT_VIEWPORT_WIDTH = int(os.getenv("PLAYWRIGHT_VIEWPORT_WIDTH", "1280"))
PLAYWRIGHT_VIEWPORT_HEIGHT = int(os.getenv("PLAYWRIGHT_VIEWPORT_HEIGHT", "720"))

# Google PageSpeed Insights API (Free - no key required for basic use)
PAGESPEED_API_URL = "https://www.googleapis.com/pagespeedonline/v5/runPagespeed"
PAGESPEED_API_KEY = os.getenv("PAGESPEED_API_KEY", "")

# SerpAPI Configuration (for real GMB data)
SERPAPI_KEY = os.getenv("SERPAPI_KEY", "")
SERPAPI_ENGINE = "google_maps"

# Industry Types for Weight Profiles
VALID_INDUSTRIES = ["saas", "restaurant", "ecommerce", "healthcare", "real_estate", "default"]

# Logging
DEBUG = os.getenv("DEBUG", "false").lower() == "true"

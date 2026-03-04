"""Configuration module for AI SEO Optimizer."""
import os
from dotenv import load_dotenv

load_dotenv()

# API Configuration
API_TITLE = "AI SEO Optimizer"
API_VERSION = "0.1.0"

# AI Service Configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
AI_MODEL = os.getenv("AI_MODEL", "gpt-4")
AI_BASE_URL = os.getenv("AI_BASE_URL", "https://api.openai.com/v1")

# Timeout Configuration
HTTP_TIMEOUT = 15
SCRAPE_TIMEOUT = 20

# Logging
DEBUG = os.getenv("DEBUG", "false").lower() == "true"

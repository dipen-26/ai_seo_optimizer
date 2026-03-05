# AI SEO Optimizer

An intelligent SEO optimization platform that provides Conversion Rate Optimization (CRO) and Google My Business (GMB) audits powered by AI. Built with FastAPI backend and modern frontend UI.

## Features

- **CRO Audits**: Analyze websites for conversion rate optimization opportunities
- **GMB Audits**: Audit and optimize Google My Business profiles
- **AI-Powered Analysis**: Leverages advanced AI models for intelligent recommendations
- **Real-time Scraping**: Fetches and analyzes website content dynamically
- **RESTful API**: Comprehensive backend API for integrations
- **User-friendly Interface**: Interactive web UI for easy access

---

## Setup Instructions

### Step 1: Clone the Repository

```bash
git clone https://github.com/dipen-26/ai_seo_optimizer.git
cd ai_seo_optimizer
```

### Step 2: Set Up the Backend

#### Step 2.1: Navigate to Backend Directory

```bash
cd backend
```

#### Step 2.2: Create a Python Virtual Environment

Create a virtual environment to isolate project dependencies:

```bash
python -m venv venv
```

#### Step 2.3: Activate the Virtual Environment

**On Windows (Command Prompt):**
```bash
venv\Scripts\activate
```

**On Windows (PowerShell):**
```bash
venv\Scripts\Activate.ps1
```

**On macOS/Linux:**
```bash
source venv/bin/activate
```

After activation, you should see `(venv)` at the beginning of your terminal prompt.

#### Step 2.4: Install Python Dependencies

```bash
pip install -r requirements.txt
```

This will install all required packages including FastAPI, Uvicorn, BeautifulSoup, Playwright, and more.

#### Step 2.5: Set Up Environment Variables

Copy the example environment file:

```bash
copy .env.example .env
```

Or on macOS/Linux:
```bash
cp .env.example .env
```

Open the `.env` file in your text editor and configure the required variables:

```env
API_TITLE=AI SEO Optimizer
API_VERSION=0.2.0

OPENROUTER_API_KEY=your_openrouter_api_key_here

AI_MODEL=deepseek/deepseek-chat

HTTP_TIMEOUT=30
SCRAPE_TIMEOUT=45

PLAYWRIGHT_TIMEOUT=45000

DEBUG=false
```

**Important**: Replace `your_openrouter_api_key_here` with your actual OpenRouter API key. Get one from [OpenRouter](https://openrouter.ai/).

#### Step 2.6: Initialize Playwright (for web scraping)

```bash
playwright install
```

This downloads browser binaries needed for web scraping.

#### Step 2.7: Run the Backend Server

```bash
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

The backend will start at: **http://127.0.0.1:8000**

You can access the API documentation at: **http://127.0.0.1:8000/docs**

---

## Project Structure

```
ai-seo-optimizer/
├── backend/
│   ├── app/
│   │   ├── api/                    # API routes
│   │   │   ├── cro_routes.py      # CRO endpoints
│   │   │   └── gmb_routes.py      # GMB endpoints
│   │   ├── services/               # Business logic
│   │   │   ├── cro_service.py
│   │   │   ├── gmb_service.py
│   │   │   ├── cro_scoring_service.py
│   │   │   ├── gmb_scoring_service.py
│   │   │   └── ai_service.py
│   │   ├── schemas/                # Pydantic models
│   │   │   ├── cro_schema.py
│   │   │   └── gmb_schema.py
│   │   ├── utils/                  # Utility functions
│   │   │   ├── data_extractor.py
│   │   │   ├── gmb_data_extractor.py
│   │   │   ├── validators.py
│   │   │   ├── viewport_detector.py
│   │   │   └── web_scraper.py
│   │   ├── core/
│   │   │   └── config.py           # Configuration
│   │   └── main.py                 # FastAPI app entry point
│   ├── requirements.txt             # Python dependencies
│   ├── .env.example                # Environment template
│   └── .env                        # Environment variables (create from .env.example)
│
├── frontend/
│   ├── index.html                  # Main HTML file
│   ├── README.md                   # Frontend documentation
│   └── assets/
│       ├── css/
│       │   └── styles.css
│       └── js/
│           └── api.js
│
└── README.md                       # This file
```

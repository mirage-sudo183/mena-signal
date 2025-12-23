# MENA Signal

A simple script to fetch yesterday's AI startup funding news from RSS feeds.

## Setup

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

## Usage

```bash
python fetch_funding_news.py
```

## Output

The script fetches funding news from:
- TechCrunch AI
- TechCrunch Startups  
- VentureBeat AI
- Crunchbase News

It filters for articles containing funding-related keywords and extracts funding amounts when available.

## Example Output

```
============================================================
AI STARTUP FUNDING NEWS
Date: December 22, 2025
============================================================

Found 3 funding news items:

1. Alphabet to buy Intersect Power to bypass energy grid bottlenecks [$4.75B]
   Source: TechCrunch AI
   https://techcrunch.com/2025/12/22/...
```

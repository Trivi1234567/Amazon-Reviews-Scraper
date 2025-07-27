"""
Pull Amazon reviews for the ASINs below via Oxylabs' Selenium scraper.
Runs headless on GitHub Actions without Poetry or proxies.
"""

from datetime import date
from pathlib import Path
import os, random, shutil
import amazon_review_scraper.scraper as ox       # Oxylabs class
from amazon_review_scraper.scraper import AmazonReviewScraper

# ── 1 ▸ Patch the proxy routine and the empty-list random.choice call ──────
def _dummy_proxy_generator(self):
    return [None]              # non-empty list avoids IndexError
ox.AmazonReviewScraper.proxy_generator = _dummy_proxy_generator
_original_choice = random.choice
random.choice = lambda seq: seq[0]               # first (and only) element
# ───────────────────────────────────────────────────────────────────────────

PRODUCTS = [
    {"asin": "B0DZZWMB2L", "domain": "amazon.com"},
    {"asin": "B071F2VLQT", "domain": "amazon.ca"},
]

OUT = Path("outputs"); OUT.mkdir(exist_ok=True)
today = date.today().isoformat()

def run(asin: str, domain: str):
    os.environ["AMAZON_DOMAIN"] = domain         # scraper now honours this
    scraper = AmazonReviewScraper()
    df = scraper.scrape_amazon_reviews(asin)
    tmp = Path("amazon_reviews.csv")             # Oxylabs always writes here
    out_file = OUT / f"{domain.replace('.', '_')}_{asin}_{today}.csv"
    shutil.move(tmp, out_file)
    print(f"✓  {out_file.name}  ({len(df)} rows)")

for item in PRODUCTS:
    run(item["asin"], item["domain"])

# restore random.choice (defensive)
random.choice = _original_choice

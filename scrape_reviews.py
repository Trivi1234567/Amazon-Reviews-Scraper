"""
Pulls the latest Amazon reviews for two ASINs every run.
✓ Uses Oxylabs’ Selenium scraper
✓ No proxies, Poetry or Makefile headaches
✓ Works head-less on GitHub Actions free runners
"""

from datetime import date
from pathlib import Path
import os, shutil, random
from selenium.webdriver.chrome.options import Options
import amazon_review_scraper.scraper as ox  # library lives in the repo we pip-installed

# ─── Patch the proxy routine & random.choice that expect a non-empty list ───
def _dummy_proxy_generator(self):           # returns one fake entry
    return [None]

ox.AmazonReviewScraper.proxy_generator = _dummy_proxy_generator
_random_choice_orig = random.choice
random.choice = lambda seq: seq[0]          # pick first element even if it's None
# ────────────────────────────────────────────────────────────────────────────

PRODUCTS = [
    {"asin": "B0DZZWMB2L", "domain": "amazon.com"},
    {"asin": "B071F2VLQT", "domain": "amazon.ca"},
]

OUT = Path("outputs"); OUT.mkdir(exist_ok=True)
today = date.today().isoformat()

def run_one(asin: str, domain: str):
    os.environ["AMAZON_DOMAIN"] = domain            # Oxylabs URL builder reads this
    # Force Chrome flags that work in CI
    Options().add_argument("--no-sandbox")
    Options().add_argument("--disable-dev-shm-usage")
    scraper = ox.AmazonReviewScraper()
    df = scraper.scrape_amazon_reviews(asin)        # returns pandas DF
    src = Path("amazon_reviews.csv")                # library always names file like this
    dst = OUT / f"{domain.replace('.', '_')}_{asin}_{today}.csv"
    shutil.move(src, dst)
    print(f"✓  {dst.name}  ({len(df)} rows)")

for prod in PRODUCTS:
    run_one(prod["asin"], prod["domain"])

# restore random.choice just in case
random.choice = _random_choice_orig

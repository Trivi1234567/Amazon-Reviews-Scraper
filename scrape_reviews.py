"""
Scrape reviews for two ASINs with Oxylabs' Selenium scraper.
Uses Selenium-Manager (no webdriver-manager) + CI-friendly Chrome flags.
"""

from datetime import date
from pathlib import Path
import os, random, shutil, time
import selenium.webdriver as sel
from selenium.webdriver.chrome.options import Options
from amazon_review_scraper.scraper import AmazonReviewScraper

# ── 1 ▸ monkey-patch the obsolete proxy routine *inside* the class ──────────
def _dummy_proxy_generator(self):           # avoid free-proxy scrape
    return [None]                           # non-empty to keep .choice() happy
AmazonReviewScraper.proxy_generator = _dummy_proxy_generator

# also patch random.choice just while the scraper is constructed
_orig_choice = random.choice
random.choice = lambda seq: seq[0]          # pick first element (None)
# ────────────────────────────────────────────────────────────────────────────

PRODUCTS = [
    {"asin": "B0DZZWMB2L", "domain": "amazon.com"},
    {"asin": "B071F2VLQT", "domain": "amazon.ca"},
]

OUT = Path("outputs")
OUT.mkdir(exist_ok=True)
stamp = date.today().isoformat()

def chrome_opts() -> Options:
    o = Options()
    o.add_argument("--headless=new")        # CI-friendly headless mode
    o.add_argument("--no-sandbox")          # required on GH runners :contentReference[oaicite:2]{index=2}
    o.add_argument("--disable-dev-shm-usage")
    return o

for prod in PRODUCTS:
    os.environ["AMAZON_DOMAIN"] = prod["domain"]   # library uses this env var
    scraper = AmazonReviewScraper()
    # patch the driver build so it uses Selenium-Manager automatically
    scraper._init_chrome_driver = lambda: sel.Chrome(options=chrome_opts())
    df = scraper.scrape_amazon_reviews(prod["asin"])   # returns pandas DF

    src = Path("amazon_reviews.csv")                   # library output file
    dst = OUT / f"{prod['domain'].replace('.', '_')}_{prod['asin']}_{stamp}.csv"
    shutil.move(src, dst)
    print(f"✓  {dst.name}  ({len(df)} rows)")
    time.sleep(1)

# restore random.choice (defensive)
random.choice = _orig_choice

"""
Weekly Amazon-review puller for two ASINs (US + CA)

▸ Pure requests/BS4 – no Selenium, proxies, or paid APIs
▸ Runs entirely in free GitHub-Actions minutes
"""

from datetime import date
from pathlib import Path
import time
import random
import pandas as pd
import amazon_product_review_scraper as aprs

# ── 1  Patch the proxy routine so it skips scraping free-proxy-list ─────────
def _noop_proxy_generator(self):
    """Return an empty proxy list; we don't need proxies for tiny volume."""
    return []

aprs.proxy_generator = _noop_proxy_generator
# ────────────────────────────────────────────────────────────────────────────

PRODUCTS = [
    {"asin": "B0DZZWMB2L", "site": "amazon.com"},
    {"asin": "B071F2VLQT", "site": "amazon.ca"},
]

OUT = Path("outputs")
OUT.mkdir(exist_ok=True)
stamp = date.today().isoformat()

for p in PRODUCTS:
    # ── 2  Temporarily monkey-patch random.choice so empty list → None ——––
    _orig_choice = random.choice

    def _safe_choice(seq):
        return None if len(seq) == 0 else _orig_choice(seq)

    random.choice = _safe_choice
    # ----------------------------------------------------------------------

    try:
        scraper = aprs.amazon_product_review_scraper(
            amazon_site=p["site"],
            product_asin=p["asin"],
            sleep_time=2,       # respectful delay between pages
            start_page=1,
            end_page=None       # keep paging until reviews stop
        )
    finally:
        random.choice = _orig_choice   # ALWAYS restore

    df: pd.DataFrame = scraper.scrape()
    outfile = OUT / f'{p["site"].replace(".", "_")}_{p["asin"]}_{stamp}.csv'
    df.to_csv(outfile, index=False)
    print(f"✓  Saved {len(df):>3} reviews → {outfile}")
    time.sleep(1)   # tiny pause between products

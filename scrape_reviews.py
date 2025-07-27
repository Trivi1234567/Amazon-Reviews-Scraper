"""
Weekly Amazon-review puller for two ASINs (US + CA).
Lives entirely inside a free GitHub Action runner – no Selenium, no proxies.
"""

from datetime import date
from pathlib import Path
import pandas as pd
import types

# ── 1. monkey-patch the broken proxy code ────────────────────────────────────
import amazon_product_review_scraper.amazon_product_review_scraper as aprs

def _noop_proxy_generator(self):
    """Return an empty proxy list instead of scraping free-proxy-list.net"""
    return []

aprs.amazon_product_review_scraper.proxy_generator = _noop_proxy_generator
# ---------------------------------------------------------------------------

PRODUCTS = [
    {"asin": "B0DZZWMB2L", "site": "amazon.com"},
    {"asin": "B071F2VLQT", "site": "amazon.ca"},
]

OUT = Path("outputs");  OUT.mkdir(exist_ok=True)
stamp = date.today().isoformat()

for p in PRODUCTS:
    scraper = aprs.amazon_product_review_scraper(  # create patched instance
        amazon_site=p["site"],
        product_asin=p["asin"],
        max_reviews=40               # page 1 is usually ±20; safe upper bound
    )
    df: pd.DataFrame = scraper.scrape()
    out_file = OUT / f'{p["site"].replace(".","_")}_{p["asin"]}_{stamp}.csv'
    df.to_csv(out_file, index=False)
    print(f"✓ {len(df)} reviews → {out_file}")

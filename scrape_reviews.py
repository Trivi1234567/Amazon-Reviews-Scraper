"""
Weekly Amazon-review puller for two ASINs (US + CA).
✓ Pure requests/BS4  ▸ no proxies, no Selenium, no Poetry
✓ Runs inside free GitHub Actions minutes
"""

from datetime import date
from pathlib import Path
import pandas as pd
import amazon_product_review_scraper as aprs   # ← single import

# ────── patch the broken proxy routine ────────────────────────────────────
def _noop_proxy_generator(self):
    """Skip scraping free-proxy-list.net (layout changed in May-2025)."""
    return []

aprs.proxy_generator = _noop_proxy_generator       # ← patch in place
# ──────────────────────────────────────────────────────────────────────────

PRODUCTS = [
    {"asin": "B0DZZWMB2L", "site": "amazon.com"},
    {"asin": "B071F2VLQT", "site": "amazon.ca"},
]

OUT = Path("outputs")
OUT.mkdir(exist_ok=True)
stamp = date.today().isoformat()

for p in PRODUCTS:
    scraper = aprs.amazon_product_review_scraper(
        amazon_site=p["site"],
        product_asin=p["asin"],
        max_reviews=40,         # one page ≈ 20 — plenty of head-room
        sleep_time=2            # polite delay between pages
    )
    df: pd.DataFrame = scraper.scrape()
    outfile = OUT / f'{p["site"].replace(".","_")}_{p["asin"]}_{stamp}.csv'
    df.to_csv(outfile, index=False)
    print(f"✓ Saved {len(df):>3} reviews → {outfile}")

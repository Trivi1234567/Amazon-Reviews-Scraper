"""
Weekly Amazon-review puller for two ASINs (US + CA).

▸ Pure requests + BeautifulSoup   ▸ No proxies, Selenium or Poetry
"""

from datetime import date
from pathlib import Path
import pandas as pd
import amazon_product_review_scraper as aprs   # package import

# ─── 1. patch the obsolete proxy routine ────────────────────────────────────
def _noop_proxy_generator(self):
    """Skip scraping free-proxy-list.net (layout changed, returns None)."""
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
    scraper = aprs.amazon_product_review_scraper(
        amazon_site=p["site"],
        product_asin=p["asin"],
        sleep_time=2,        # 2-second pause between pages
        start_page=1,
        end_page=None        # scrape until no more pages (≃ 40 reviews max)
    )
    df: pd.DataFrame = scraper.scrape()
    outfile = OUT / f'{p["site"].replace(".", "_")}_{p["asin"]}_{stamp}.csv'
    df.to_csv(outfile, index=False)
    print(f"✓  Saved {len(df):>3} reviews → {outfile}")

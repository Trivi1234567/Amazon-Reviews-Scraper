"""
Weekly Amazon-review puller for two ASINs (US + CA).

✓ 100 % self-hosted  ▸ no Selenium, Chromium, proxies, or paid APIs
✓ Runs inside free GitHub-Actions minutes (public repo ⇒ unlimited)
"""

from datetime import date
from pathlib import Path
import pandas as pd
import amazon_product_review_scraper as aprs       # 3-rd-party pkg

# ──────────────────────────────────────────────────────────────────────────
# 1) Monkey-patch the BROKEN proxy routine INSIDE the scraper class
#    so it returns an empty list instead of scraping free-proxy-list.net
#    (the site layout changed in May-2025 and now returns None).  :contentReference[oaicite:1]{index=1}
# ──────────────────────────────────────────────────────────────────────────
def _noop_proxy_generator(self):
    """Return no proxies; direct requests are fine for <100 reviews."""
    return []

# The public API object is actually a class; patch its method:
setattr(aprs.amazon_product_review_scraper, "proxy_generator", _noop_proxy_generator)
# ──────────────────────────────────────────────────────────────────────────

PRODUCTS = [
    {"asin": "B0DZZWMB2L", "site": "amazon.com"},   # U S
    {"asin": "B071F2VLQT", "site": "amazon.ca"},    # Canada
]

OUT = Path("outputs")
OUT.mkdir(exist_ok=True)
stamp = date.today().isoformat()

for p in PRODUCTS:
    scraper = aprs.amazon_product_review_scraper(
        amazon_site=p["site"],
        product_asin=p["asin"],
        sleep_time=2,          # polite 2-s pause between pages
        start_page=1,
        end_page=None          # scrape until pages run out
    )
    df: pd.DataFrame = scraper.scrape()
    outfile = OUT / f'{p["site"].replace(".", "_")}_{p["asin"]}_{stamp}.csv'
    df.to_csv(outfile, index=False)
    print(f"✓  Saved {len(df):>3} reviews → {outfile}")

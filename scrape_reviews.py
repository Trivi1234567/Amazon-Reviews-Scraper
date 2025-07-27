"""
Lightweight weekly scraper for two ASINs (US + CA).
Outputs one CSV per product inside ./outputs/.
"""

from datetime import date
from pathlib import Path
import pandas as pd
from amazon_product_review_scraper import amazon_product_review_scraper

PRODUCTS = [
    {"asin": "B0DZZWMB2L", "site": "amazon.com"},
    {"asin": "B071F2VLQT", "site": "amazon.ca"},
]

OUT = Path("outputs")
OUT.mkdir(exist_ok=True)
stamp = date.today().isoformat()

for p in PRODUCTS:
    df = (
        amazon_product_review_scraper(amazon_site=p["site"], product_asin=p["asin"])
        .scrape()
    )
    out_file = OUT / f'{p["site"].replace(".","_")}_{p["asin"]}_{stamp}.csv'
    df.to_csv(out_file, index=False)
    print(f"✓  Saved {len(df)} reviews → {out_file}")

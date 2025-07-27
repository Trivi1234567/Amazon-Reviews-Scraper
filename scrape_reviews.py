from datetime import date
from pathlib import Path
import subprocess, shutil, os

PRODUCTS = [
    {"asin": "B0DZZWMB2L", "domain": "amazon.com"},
    {"asin": "B071F2VLQT", "domain": "amazon.ca"},
]

OUT_DIR = Path("outputs")
OUT_DIR.mkdir(exist_ok=True)
TODAY = date.today().isoformat()

def run_one(asin, domain):
    env = os.environ.copy()
    env["AMAZON_DOMAIN"] = domain              # scraper reads this
    subprocess.run(
        ["make", "scrape", f'ASIN_CODE="{asin}"'],
        cwd="amazon-review-scraper",
        check=True,
        env=env,
    )
    src = Path("amazon-review-scraper") / "amazon_reviews.csv"
    dst = OUT_DIR / f"{domain.replace('.', '_')}_{asin}_{TODAY}.csv"
    shutil.move(src, dst)

for p in PRODUCTS:
    run_one(p["asin"], p["domain"])

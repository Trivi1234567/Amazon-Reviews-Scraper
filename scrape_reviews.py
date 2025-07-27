-from selenium.webdriver.chrome.service import Service
-from selenium.webdriver.common.by import By
+# ――― Selenium bits ―――――――――――――――――――――――――――――――――
+from selenium.webdriver.chrome.service import Service
+from selenium.webdriver.common.by import By
+from selenium.webdriver.remote.webelement import WebElement   # ← ADD THIS


"""
Run the Oxylabs Selenium scraper for a fixed list of ASIN/domain pairs
and save each run as a dated CSV in ./outputs/.
"""

from datetime import date
from pathlib import Path
import subprocess, shutil, os, sys

ROOT = Path(__file__).parent                    # repo root in GitHub Actions
SCRAPER_DIR = ROOT / "amazon-review-scraper-main"
if not SCRAPER_DIR.exists():
    sys.exit(f"❌  Folder {SCRAPER_DIR} not found. Check repo layout.")

PRODUCTS = [
    {"asin": "B0DZZWMB2L", "domain": "amazon.com"},
    {"asin": "B071F2VLQT", "domain": "amazon.ca"},
]

OUT_DIR = ROOT / "outputs"
OUT_DIR.mkdir(exist_ok=True)
TODAY = date.today().isoformat()

def run_one(asin: str, domain: str) -> None:
    env = os.environ.copy()
    env["AMAZON_DOMAIN"] = domain              # scraper.py reads this
    subprocess.run(
        ["make", "scrape", f'ASIN_CODE=\"{asin}\"'],
        cwd=SCRAPER_DIR,
        check=True,
        env=env,
    )
    src = SCRAPER_DIR / "amazon_reviews.csv"
    dst = OUT_DIR / f"{domain.replace('.', '_')}_{asin}_{TODAY}.csv"
    shutil.move(src, dst)

for p in PRODUCTS:
    run_one(p["asin"], p["domain"])

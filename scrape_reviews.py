"""
Module for scraping Amazon reviews.
"""

import logging
import os
import time
from typing import List

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement  # important!
from webdriver_manager.chrome import ChromeDriverManager

from amazon_review_scraper.models import Review

# Silence webdriver-manager’s INFO logs
logging.getLogger("WDM").setLevel(logging.ERROR)


class DriverInitializationError(Exception):
    """Raised when Chrome webdriver cannot be initialised."""


class DriverGetReviewsError(Exception):
    """Raised when review data cannot be scraped from Amazon."""


class AmazonReviewScraper:
    """Scrapes review data for a single Amazon product."""

    def __init__(self, logger: logging.Logger | None = None) -> None:
        self._logger = logger or logging.getLogger(__name__)

    # ──────────────────────────────────────────────────────────────────────
    # Internals
    # ──────────────────────────────────────────────────────────────────────
    def _init_chrome_driver(self) -> webdriver.Chrome:
        """Spin up a headless Chrome driver."""
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        service = Service(ChromeDriverManager().install())
        return webdriver.Chrome(service=service, options=chrome_options)

    @staticmethod
    def _parse_review_data(review_el: WebElement) -> Review:
        """Convert a single <div class='review'> node into a Review dataclass."""
        author = review_el.find_element(By.CLASS_NAME, "a-profile-name").text
        content = review_el.find_element(By.CLASS_NAME, "reviewText").text

        rating_text = (
            review_el.find_element(By.CLASS_NAME, "review-rating")
            .find_element(By.CLASS_NAME, "a-icon-alt")
            .get_attribute("innerHTML")
        )
        rating = float(rating_text.split(" out of ")[0])

        title = (
            review_el.find_element(By.CLASS_NAME, "review-title-content")
            .find_element(By.TAG_NAME, "span")
            .text
        )

        return Review(author=author, content=content, rating=rating, title=title)

    def _get_reviews_from_product_page(
        self, url: str, driver: webdriver.Chrome
    ) -> List[Review]:
        """Loads the product review URL and extracts all reviews on page 1."""
        driver.get(url)
        time.sleep(3)  # allow lazy elements to render

        reviews_raw = driver.find_elements(By.CLASS_NAME, "review")
        reviews: List[Review] = []
        for raw in reviews_raw:
            try:
                reviews.append(self._parse_review_data(raw))
            except Exception:  # noqa: BLE001
                self._logger.exception(
                    "Unexpected error parsing a review; skipping that entry."
                )
        return reviews

    # ──────────────────────────────────────────────────────────────────────
    # Public API
    # ──────────────────────────────────────────────────────────────────────
    def scrape_amazon_reviews(self, asin_code: str) -> List[Review]:
        """
        Return a list of Review objects for the given ASIN.

        Raises
        ------
        DriverInitializationError
            If the Chrome webdriver cannot be started.
        DriverGetReviewsError
            If scraping fails for any other reason.
        """
        self._logger.info("Scraping reviews for ASIN %s …", asin_code)

        try:
            driver = self._init_chrome_driver()
        except Exception as exc:  # noqa: BLE001
            raise DriverInitializationError from exc

        # Build region-aware reviews URL
        domain = os.getenv("AMAZON_DOMAIN", "amazon.com")
        url = f"https://www.{domain}/product-reviews/{asin_code}"

        try:
            return self._get_reviews_from_product_page(url, driver)
        except Exception as exc:  # noqa: BLE001
            raise DriverGetReviewsError from exc
        finally:
            driver.quit()

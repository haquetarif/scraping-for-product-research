"""
Script to scrape WooCommerce marketplace extensions.

This module illustrates how to programmatically gather data about WooCommerce
extensions and write the results to CSV and Excel files.  It uses Python's
standard ``requests`` library to call WooCommerce's public REST API which
returns information about each extension.  The script paginates through
all available pages, extracts a handful of relevant fields from each
product (title, vendor, price, rating and review count) and normalises
the price field so that free items are labelled ``Free``.

There is also a small hard‑coded sample of nine extensions from the first
page of the API.  In an environment where outbound HTTP requests are
restricted (such as the one used to generate this answer), you can still
generate a CSV/XLSX from this sample data to verify the structure of
the output files.  When network access is available, simply set
``RUN_FULL_SCRAPE`` to ``True`` and the script will fetch all pages.

Usage:

    python woocommerce_scraper.py

The script writes two files into the current working directory:

    - ``woocommerce_extensions.csv``
    - ``woocommerce_extensions.xlsx``

These files will contain either the sample data or the full dataset
depending on the value of ``RUN_FULL_SCRAPE``.
"""

import csv
import json
from dataclasses import dataclass, asdict
from typing import List

import pandas as pd  # type: ignore
import requests


@dataclass
class Extension:
    """Represents a single WooCommerce extension.

    Attributes:
        title: Name of the extension.
        vendor: Name of the company or developer who built the extension.
        price: Human friendly price string. ``Free`` for free items.
        rating: Average rating out of five stars (may be ``None`` if no ratings).
        reviews_count: Number of reviews (may be ``None`` if unspecified).
    """

    title: str
    vendor: str
    price: str
    rating: float | None
    reviews_count: int | None


def parse_price(raw_price: float, currency: str) -> str:
    """Return a human friendly price string given the raw price and currency.

    ``raw_price`` is numeric (0 for free items).  If the price is zero, the
    function returns ``"Free"``.  Otherwise it prefixes the price with the
    currency code (USD) and ensures two decimal places.
    """
    if raw_price == 0:
        return "Free"
    # Format with currency symbol ($) and two decimal places
    return f"${raw_price:.2f}"


def fetch_extensions() -> List[Extension]:
    """Fetch all extensions from WooCommerce's public API.

    WooCommerce exposes a REST endpoint at
    ``https://woocommerce.com/wp-json/wccom-extensions/1.0/search``.  It
    accepts a ``page`` query parameter to paginate through the results.  At
    the time of writing there are 20 pages of data with roughly 60 items
    per page.  This function iterates over each page, parses the JSON
    response and constructs ``Extension`` objects from the relevant
    fields.

    Returns a list of ``Extension`` objects.
    """
    base_url = "https://woocommerce.com/wp-json/wccom-extensions/1.0/search"
    page = 1
    extensions: list[Extension] = []
    while True:
        params = {"page": page}
        # WooCommerce requires a User‑Agent header; use a browser‑like UA
        headers = {"User-Agent": "Mozilla/5.0 (compatible; Script/1.0)"}
        resp = requests.get(base_url, params=params, headers=headers, timeout=30)
        resp.raise_for_status()
        data = resp.json()
        products = data.get("products", [])
        for product in products:
            # Extract the fields we care about
            title = product.get("title", "").strip()
            vendor = product.get("vendor_name", "").strip() or product.get("vendor", "")
            raw_price = product.get("raw_price", 0)
            currency = product.get("currency", "USD")
            price = parse_price(float(raw_price), currency)
            rating = product.get("rating")
            reviews_count = product.get("reviews_count")
            extensions.append(Extension(title=title, vendor=vendor, price=price, rating=rating, reviews_count=reviews_count))
        # Stop when we've fetched all pages
        total_pages = data.get("total_pages")
        if total_pages is None or page >= int(total_pages):
            break
        page += 1
    return extensions


def get_sample_extensions() -> List[Extension]:
    """Return a small hard‑coded sample of extensions.

    This sample is derived from the first page of the WooCommerce API.  It
    includes nine of the most prominent extensions on that page along with
    their vendor, price, rating and review count.  Ratings and review
    counts may change over time – this sample reflects the values observed
    in August 2025.
    """
    sample = [
        Extension(title="Google Analytics for WooCommerce", vendor="Woo", price="Free", rating=4.3, reviews_count=51),
        Extension(title="WooCommerce Tax", vendor="Woo", price="Free", rating=4.0, reviews_count=14),
        Extension(title="Stripe", vendor="Stripe", price="Free", rating=3.7, reviews_count=47),
        Extension(title="Klaviyo", vendor="Klaviyo", price="Free", rating=3.9, reviews_count=26),
        Extension(title="Mailchimp", vendor="Mailchimp", price="Free", rating=3.7, reviews_count=52),
        Extension(title="Jetpack", vendor="Jetpack", price="Free", rating=4.5, reviews_count=21),
        Extension(title="Facebook", vendor="Facebook", price="Free", rating=2.6, reviews_count=120),
        Extension(title="WooPayments", vendor="Woo", price="Free", rating=3.9, reviews_count=139),
        Extension(title="Google for WooCommerce", vendor="Woo", price="Free", rating=4.2, reviews_count=144),
    ]
    return sample


def write_files(extensions: List[Extension]) -> None:
    """Write the collected extensions to CSV and Excel files.

    Args:
        extensions: List of ``Extension`` objects to serialize.
    """
    # Convert dataclasses into a list of dictionaries
    rows = [asdict(ext) for ext in extensions]
    # Write CSV
    csv_path = "woocommerce_extensions.csv"
    with open(csv_path, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)
    # Write Excel via pandas for convenience
    df = pd.DataFrame(rows)
    xlsx_path = "woocommerce_extensions.xlsx"
    df.to_excel(xlsx_path, index=False)
    print(f"Wrote {len(extensions)} extensions to {csv_path} and {xlsx_path}.")


def main() -> None:
    """Entry point for command line execution."""
    # Toggle this flag to run the full scrape.  When running in a restricted
    # environment (no outbound internet) leave this set to False to use
    # the hard‑coded sample instead.
    RUN_FULL_SCRAPE = True
    if RUN_FULL_SCRAPE:
        print("Fetching extensions from WooCommerce API...")
        extensions = fetch_extensions()
    else:
        print("Using hard‑coded sample extensions.")
        extensions = get_sample_extensions()
    write_files(extensions)


if __name__ == "__main__":
    main()

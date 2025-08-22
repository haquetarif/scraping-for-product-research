"""
Scrape WooCommerce marketplace extensions (now includes Description).

Outputs:
  - woocommerce_extensions.csv
  - woocommerce_extensions.xlsx
"""

import csv
import re
import html
from dataclasses import dataclass, asdict
from typing import List, Optional

import pandas as pd
import requests


@dataclass
class Extension:
    title: str
    vendor: str
    price: str
    rating: Optional[float]
    reviews_count: Optional[int]
    description: str  # NEW


def strip_html(text: str) -> str:
    """Remove HTML tags and collapse whitespace."""
    if not text:
        return ""
    # unescape first so entities inside tags don’t throw regex off
    t = html.unescape(text)
    # drop tags
    t = re.sub(r"<[^>]+>", " ", t)
    # collapse whitespace
    t = re.sub(r"\s+", " ", t).strip()
    return t


def parse_price(raw_price: float, currency: str) -> str:
    if raw_price == 0:
        return "Free"
    return f"${float(raw_price):.2f}"


def best_description(product: dict) -> str:
    """
    Pick the best description text from common Woo marketplace fields.
    We try several keys because the API can vary.
    """
    candidates = [
        "excerpt_html", "excerpt",
        "short_description", "short_description_html",
        "description", "description_html",
        "content", "content_html",
    ]
    for key in candidates:
        val = product.get(key)
        if isinstance(val, str) and val.strip():
            return strip_html(val)
    return ""


def fetch_extensions() -> List[Extension]:
    base_url = "https://woocommerce.com/wp-json/wccom-extensions/1.0/search"
    page = 1
    extensions: List[Extension] = []
    headers = {"User-Agent": "Mozilla/5.0 (compatible; Script/1.0)"}

    while True:
        resp = requests.get(base_url, params={"page": page}, headers=headers, timeout=30)
        resp.raise_for_status()
        data = resp.json()

        products = data.get("products", [])
        for product in products:
            title = (product.get("title") or "").strip()
            vendor = (product.get("vendor_name") or product.get("vendor") or "").strip()
            raw_price = product.get("raw_price", 0)
            currency = product.get("currency", "USD")
            price = parse_price(float(raw_price), currency)
            rating = product.get("rating")
            reviews_count = product.get("reviews_count")
            description = best_description(product)

            extensions.append(
                Extension(
                    title=title,
                    vendor=vendor,
                    price=price,
                    rating=rating,
                    reviews_count=reviews_count,
                    description=description,
                )
            )

        total_pages = data.get("total_pages")
        if total_pages is None or page >= int(total_pages):
            break
        page += 1

    return extensions


def get_sample_extensions() -> List[Extension]:
    """Sample data (now with short descriptions)."""
    return [
        Extension(
            title="Google Analytics for WooCommerce",
            vendor="Woo",
            price="Free",
            rating=4.3,
            reviews_count=51,
            description="Connect your store to Google Analytics to track eCommerce performance.",
        ),
        Extension(
            title="WooCommerce Tax",
            vendor="Woo",
            price="Free",
            rating=4.0,
            reviews_count=14,
            description="Automated tax calculations for WooCommerce with minimal setup.",
        ),
        Extension(
            title="Stripe",
            vendor="Stripe",
            price="Free",
            rating=3.7,
            reviews_count=47,
            description="Accept major cards and wallets via Stripe with secure checkout.",
        ),
        Extension(
            title="Klaviyo",
            vendor="Klaviyo",
            price="Free",
            rating=3.9,
            reviews_count=26,
            description="Email & SMS marketing automation synced with your Woo orders and customers.",
        ),
        Extension(
            title="Mailchimp",
            vendor="Mailchimp",
            price="Free",
            rating=3.7,
            reviews_count=52,
            description="Sync customers and purchases to Mailchimp for targeted campaigns.",
        ),
        Extension(
            title="Jetpack",
            vendor="Jetpack",
            price="Free",
            rating=4.5,
            reviews_count=21,
            description="Security, backups, and performance tools for your Woo store.",
        ),
        Extension(
            title="Facebook",
            vendor="Facebook",
            price="Free",
            rating=2.6,
            reviews_count=120,
            description="Sync products and run ads on Facebook and Instagram.",
        ),
        Extension(
            title="WooPayments",
            vendor="Woo",
            price="Free",
            rating=3.9,
            reviews_count=139,
            description="The only payment solution fully integrated with WooCommerce. Accept credit/debit cards and local payment options with no setup or monthly fees.",
        ),
        Extension(
            title="Google for WooCommerce",
            vendor="Woo",
            price="Free",
            rating=4.2,
            reviews_count=144,
            description="Connect your catalog to Google to reach shoppers across Search and Shopping.",
        ),
    ]


def write_files(extensions: List[Extension]) -> None:
    rows = [asdict(ext) for ext in extensions]
    csv_path = "woocommerce_extensions.csv"
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)
    df = pd.DataFrame(rows)
    xlsx_path = "woocommerce_extensions.xlsx"
    df.to_excel(xlsx_path, index=False)
    print(f"Wrote {len(extensions)} extensions to {csv_path} and {xlsx_path}.")


def main() -> None:
    RUN_FULL_SCRAPE = False  # set True to hit the API
    if RUN_FULL_SCRAPE:
        print("Fetching extensions from WooCommerce API...")
        exts = fetch_extensions()
    else:
        print("Using hard-coded sample extensions.")
        exts = get_sample_extensions()
    write_files(exts)


if __name__ == "__main__":
    main()

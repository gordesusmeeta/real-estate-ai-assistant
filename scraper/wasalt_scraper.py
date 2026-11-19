
import requests
from bs4 import BeautifulSoup
import json
import re
import time
from urllib.robotparser import RobotFileParser
from pathlib import Path

BASE_URL = "https://wasalt.sa/"
OUTPUT_FILE = Path("data/raw/wasalt_properties.json")

HEADERS = {
    "User-Agent": "RealEstateAIResearchBot/1.0"
}

# Start with a small sample from the public sitemap
SAMPLE_URLS = [
    "https://wasalt.sa/en/property/sale/apartment-675-sqm-with-3-bedrooms-5879365",
    "https://wasalt.sa/en/property/sale/apartment-166635-sqm-with-2-bedrooms-5879361",
    "https://wasalt.sa/en/property/rent/apartment-11917-sqm-with-3-bedrooms-5879383"
]


def check_permission(url):
    robots_url = BASE_URL + "robots.txt"

    response = requests.get(
        robots_url,
        headers=HEADERS,
        timeout=20
    )
    response.raise_for_status()

    parser = RobotFileParser()
    parser.parse(response.text.splitlines())

    return parser.can_fetch(HEADERS["User-Agent"], url)


def extract_price(text):
    match = re.search(
        r"Price:\s*([\d,]+)\s*(SAR|ر\.س)?",
        text,
        re.IGNORECASE
    )
    return match.group(1).replace(",", "") if match else None


def extract_property(url):
    print("\nInspecting:", url)

    if not check_permission(url):
        print("Robots.txt does not permit access. Skipping.")
        return None

    try:
        response = requests.get(
            url,
            headers=HEADERS,
            timeout=25
        )

        if response.status_code != 200:
            print("HTTP error:", response.status_code)
            return None

        soup = BeautifulSoup(response.text, "html.parser")
        text = soup.get_text(" ", strip=True)

        title = soup.title.get_text(strip=True) if soup.title else None

        # Extract bedroom count
        bedroom_match = re.search(r"(\d+)\s*bedrooms", text, re.IGNORECASE)

        # Extract area
        area_match = re.search(
            r"([\d,.]+)\s*SQM",
            text,
            re.IGNORECASE
        )

        # Extract price
        price = extract_price(text)

        # Extract location from page text
        location = None
        location_match = re.search(
            r"Apartment\s+(?:for Sale|for Rent)\s+in\s+([^,]+,\s*[^.]+)",
            text,
            re.IGNORECASE
        )

        if location_match:
            location = location_match.group(1).strip()

        property_data = {
            "source": "Wasalt",
            "url": url,
            "title": title,
            "property_type": "Apartment" if "apartment" in url.lower() else "Other",
            "transaction_type": "rent" if "/rent/" in url.lower() else "sale",
            "location": location,
            "bedrooms": int(bedroom_match.group(1)) if bedroom_match else None,
            "area_sqm": area_match.group(1) if area_match else None,
            "price": price,
            "currency": "SAR",
            "description": text[:1500]
        }

        print("Extracted:", title)

        return property_data

    except requests.RequestException as error:
        print("Request failed:", error)
        return None


def main():
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

    properties = []

    for url in SAMPLE_URLS:
        data = extract_property(url)

        if data:
            properties.append(data)

        time.sleep(3)

    with open(OUTPUT_FILE, "w", encoding="utf-8") as file:
        json.dump(properties, file, indent=4, ensure_ascii=False)

    print("\n--------------------------------")
    print("Scraping completed.")
    print("Properties collected:", len(properties))
    print("Saved to:", OUTPUT_FILE)


if __name__ == "__main__":
    main()

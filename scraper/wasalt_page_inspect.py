
import requests
from urllib.robotparser import RobotFileParser
from urllib.parse import urljoin
from bs4 import BeautifulSoup

BASE_URL = "https://wasalt.sa/"
ROBOTS_URL = urljoin(BASE_URL, "robots.txt")

PROPERTY_URL = (
    "https://wasalt.sa/en/property/sale/"
    "apartment-675-sqm-with-3-bedrooms-5879365"
)

headers = {
    "User-Agent": "RealEstateAIResearchBot/1.0"
}

# 1. Check robots.txt for the actual domain
try:
    robots_response = requests.get(
        ROBOTS_URL,
        headers=headers,
        timeout=20
    )

    print("Robots status:", robots_response.status_code)

    if robots_response.status_code != 200:
        print("Cannot verify access rules. Stopping.")
        raise SystemExit

    parser = RobotFileParser()
    parser.parse(robots_response.text.splitlines())

    allowed = parser.can_fetch("*", PROPERTY_URL)

    print("Property URL permitted:", allowed)

    if not allowed:
        print("Page inspection skipped.")
        raise SystemExit

    # 2. Inspect one listing only
    response = requests.get(
        PROPERTY_URL,
        headers=headers,
        timeout=20
    )

    print("\nPage status:", response.status_code)
    print("HTML size:", len(response.content), "bytes")

    if response.status_code != 200:
        print("Page could not be accessed.")
        raise SystemExit

    soup = BeautifulSoup(response.text, "html.parser")

    print("\n--- PAGE TITLE ---")
    print(soup.title.get_text(strip=True) if soup.title else "Not found")

    print("\n--- HEADINGS ---")
    for heading in soup.find_all(["h1", "h2", "h3"]):
        text = heading.get_text(" ", strip=True)
        if text:
            print("-", text)

    print("\n--- TEXT PREVIEW ---")
    print(soup.get_text(" ", strip=True)[:1500])

except requests.RequestException as error:
    print("Request failed:", error)

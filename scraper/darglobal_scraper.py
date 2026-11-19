
import requests
from bs4 import BeautifulSoup
import json

URL = "https://darglobal.co.uk/one-of-one/project-pagani"

headers = {
    "User-Agent": "RealEstateAIResearchBot/1.0"
}

response = requests.get(URL, headers=headers, timeout=20)

print("HTTP Status:", response.status_code)
print("HTML Size:", len(response.text), "characters")

response.raise_for_status()

soup = BeautifulSoup(response.text, "html.parser")

print("\n--- PAGE METADATA ---")

print("Title:", soup.title.get_text(strip=True) if soup.title else "Not found")

for name in ["description", "og:title", "og:description"]:
    tag = (
        soup.find("meta", attrs={"name": name})
        or soup.find("meta", attrs={"property": name})
    )

    print(f"{name}:", tag.get("content", "Not found") if tag else "Not found")

print("\n--- HEADINGS ---")

for heading in soup.find_all(["h1", "h2", "h3"]):
    text = heading.get_text(" ", strip=True)
    if text:
        print("-", text)

print("\n--- JSON-LD DATA ---")

for script in soup.find_all("script", type="application/ld+json"):
    try:
        data = json.loads(script.string or script.get_text())
        print(json.dumps(data, indent=2)[:2000])
    except (json.JSONDecodeError, TypeError):
        print("Could not parse JSON-LD block")

print("\n--- PAGE TEXT PREVIEW ---")

body_text = soup.get_text(" ", strip=True)
print(body_text[:1500] if body_text else "No text found")

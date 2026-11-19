
import requests
import xml.etree.ElementTree as ET

SITEMAP_URL = "https://darglobal.co.uk/sitemap.xml"

headers = {
    "User-Agent": "Mozilla/5.0"
}

response = requests.get(
    SITEMAP_URL,
    headers=headers,
    timeout=20
)

response.raise_for_status()

root = ET.fromstring(response.content)

namespace = {
    "sm": "http://www.sitemaps.org/schemas/sitemap/0.9"
}

project_urls = []

for loc in root.findall(".//sm:loc", namespace):
    url = loc.text.strip()

    if (
        "/projects/" in url
        or "/one-of-one/" in url
    ):
        project_urls.append(url)

print("Total project URLs:", len(project_urls))

print("\n--- PROJECT URLS ---")

for index, url in enumerate(project_urls, start=1):
    print(f"{index}. {url}")

# Save discovered URLs for later processing
with open("data/project_urls.txt", "w", encoding="utf-8") as file:
    file.write("\n".join(project_urls))

print("\nURLs saved to data/project_urls.txt")

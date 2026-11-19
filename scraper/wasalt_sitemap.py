
import requests
import gzip
import xml.etree.ElementTree as ET

SITEMAPS = {
    "Property Products": "https://cdn.wasalt.sa/sitemap/product_sitemap_en_sa.xml.gz",
    "Rental Properties": "https://cdn.wasalt.sa/sitemap/rental_pdp_sitemap_en_sa.xml.gz",
    "Static Pages": "https://cdn.wasalt.sa/sitemap/static_sitemap_en_sa.xml.gz"
}

HEADERS = {
    "User-Agent": "RealEstateAIResearchBot/1.0"
}

NAMESPACE = {
    "sm": "http://www.sitemaps.org/schemas/sitemap/0.9"
}


def inspect_sitemap(name, url):
    print("\n" + "=" * 60)
    print(name)

    try:
        response = requests.get(
            url,
            headers=HEADERS,
            timeout=30
        )

        print("HTTP Status:", response.status_code)
        response.raise_for_status()

        content = response.content

        # Decompress if the downloaded file is gzip-compressed
        if content.startswith(b"\x1f\x8b"):
            content = gzip.decompress(content)

        root = ET.fromstring(content)

        urls = [
            element.text.strip()
            for element in root.findall(".//sm:loc", NAMESPACE)
            if element.text
        ]

        print("Total URLs:", len(urls))
        print("\nFirst 10 URLs:")

        for url in urls[:10]:
            print("-", url)

        return urls

    except Exception as error:
        print("Inspection failed:", error)
        return []


if __name__ == "__main__":
    for name, url in SITEMAPS.items():
        inspect_sitemap(name, url)


import requests

urls = [
    "https://wasalt.com/robots.txt",
    "https://wasalt.com/sitemap.xml"
]

headers = {
    "User-Agent": "Mozilla/5.0"
}

for url in urls:
    print("\n" + "=" * 60)
    print("Checking:", url)

    try:
        response = requests.get(
            url,
            headers=headers,
            timeout=20
        )

        print("Status:", response.status_code)
        print("Content-Type:", response.headers.get("Content-Type"))
        print("\nResponse preview:")
        print(response.text[:2500])

    except requests.RequestException as error:
        print("Request failed:", error)

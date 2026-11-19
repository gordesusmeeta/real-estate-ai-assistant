
import requests
from bs4 import BeautifulSoup

URL = "https://darglobal.co.uk/projects"

headers = {
    "User-Agent": "Mozilla/5.0"
}

try:
    response = requests.get(
        URL,
        headers=headers,
        timeout=20
    )

    print("HTTP Status:", response.status_code)
    print("HTML Size:", len(response.content))

    if response.status_code == 200:
        soup = BeautifulSoup(response.text, "html.parser")

        print("\nPage title:")
        print(
            soup.title.get_text(strip=True)
            if soup.title else "Not found"
        )

        print("\nHeadings:")

        for heading in soup.find_all(["h1", "h2", "h3"]):
            text = heading.get_text(" ", strip=True)
            if text:
                print("-", text)

        print("\nText preview:")
        print(soup.get_text(" ", strip=True)[:2000])

    else:
        print("Page unavailable for inspection.")

except requests.RequestException as error:
    print("Request failed:", error)


import json
import re
from pathlib import Path
from datetime import datetime, timezone
from urllib.parse import urlparse

# Project root directory
ROOT_DIR = Path(__file__).resolve().parent.parent

# Input and output files
INPUT_FILE = ROOT_DIR / "data" / "darglobal_public_urls.txt"
OUTPUT_FILE = ROOT_DIR / "data" / "raw" / "darglobal_projects.json"


def format_name(slug):
    """Convert a URL slug into a readable name."""
    return re.sub(r"\s+", " ", slug.replace("-", " ").replace("_", " ")).strip().title()


def extract_project_record(url):
    """Create a structured record from an official DarGlobal URL."""

    path = urlparse(url).path.strip("/")
    parts = path.split("/")

    if not parts:
        return None

    # Individual One of One project pages
    if parts[0] == "one-of-one" and len(parts) > 1:
        slug = parts[-1]

        return {
            "source": "DarGlobal",
            "record_type": "project_reference",
            "project_name": format_name(slug),
            "category": "One of One",
            "location": None,
            "url": url,
            "content_source": "Official DarGlobal sitemap",
            "details_verified": False
        }

    # Project and property category pages
    if parts[0] == "projects":
        slug = parts[-1]

        country = None
        property_type = None

        for part in parts:
            country_match = re.search(r"properties-in-(.+)", part)

            if country_match:
                country = format_name(country_match.group(1))

        if parts[-1] in ["villas", "apartments", "penthouse"]:
            property_type = format_name(parts[-1])

        # A country/type directory is not an individual project
        is_category = (
            "properties-in-" in url or
            parts[-1] in ["villas", "apartments", "penthouse"]
        )

        return {
            "source": "DarGlobal",
            "record_type": (
                "project_category" if is_category
                else "project_reference"
            ),
            "project_name": format_name(slug),
            "category": property_type,
            "location": country,
            "url": url,
            "content_source": "Official DarGlobal sitemap",
            "details_verified": False
        }

    return None


def main():
    if not INPUT_FILE.exists():
        print("ERROR: URL file not found:", INPUT_FILE)
        return

    with open(INPUT_FILE, "r", encoding="utf-8") as file:
        content = file.read()

    # Extract URLs even if the file contains headings or bullet points
    urls = re.findall(r"https?://[^\s]+", content)

    # Remove duplicate URLs and trailing punctuation
    urls = list(dict.fromkeys(
        url.rstrip(".,;)")
        for url in urls
    ))

    records = []

    for url in urls:
        record = extract_project_record(url)

        if record:
            records.append(record)

    # Create output directory if necessary
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

    with open(OUTPUT_FILE, "w", encoding="utf-8") as file:
        json.dump(records, file, indent=4, ensure_ascii=False)

    individual_projects = sum(
        record["record_type"] == "project_reference"
        for record in records
    )

    categories = sum(
        record["record_type"] == "project_category"
        for record in records
    )

    print("\n========== DARGLOBAL DATA SUMMARY ==========")
    print("Total records:", len(records))
    print("Project references:", individual_projects)
    print("Project categories:", categories)
    print("Verified property details: 0")
    print("Saved to:", OUTPUT_FILE)


if __name__ == "__main__":
    main()

print("\n--- PAGE TEXT PREVIEW ---")

body_text = soup.get_text(" ", strip=True)
print(body_text[:1500] if body_text else "No text found")

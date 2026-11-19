
import json
import re
from pathlib import Path
from urllib.parse import urlparse

INPUT_FILE = Path("data/project_urls.txt")
OUTPUT_FILE = Path("data/raw/darglobal_projects.json")


def clean_slug(url):
    path = urlparse(url).path
    slug = path.rstrip("/").split("/")[-1]

    slug = re.sub(r"-\d+$", "", slug)
    return slug.replace("-", " ").title()


def main():
    if not INPUT_FILE.exists():
        print("Project URL file not found.")
        return

    urls = INPUT_FILE.read_text(encoding="utf-8").splitlines()

    projects = []

    for url in urls:
        if not url.strip():
            continue

        project = {
            "source": "DarGlobal",
            "url": url,
            "project_name": clean_slug(url),
            "information_source": "Public sitemap URL",
            "details_verified": False
        }

        projects.append(project)

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

    with open(OUTPUT_FILE, "w", encoding="utf-8") as file:
        json.dump(projects, file, indent=4, ensure_ascii=False)

    print("DarGlobal URL records:", len(projects))
    print("Saved to:", OUTPUT_FILE)

    print("\nFirst 5 records:")
    for project in projects[:5]:
        print(project["project_name"])


if __name__ == "__main__":
    main()

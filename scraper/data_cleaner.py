
import json
from pathlib import Path

WASALT_FILE = Path("data/raw/wasalt_properties.json")
DARGLOBAL_FILE = Path("data/raw/darglobal_projects.json")
OUTPUT_FILE = Path("data/processed/real_estate_data.json")


def load_json(path):
    if not path.exists():
        print(f"File not found: {path}")
        return []

    with open(path, "r", encoding="utf-8") as file:
        return json.load(file)


def clean_wasalt(properties):
    cleaned = []

    for item in properties:
        cleaned.append({
            "source": "Wasalt",
            "record_type": "property_listing",
            "title": item.get("title"),
            "property_type": item.get("property_type"),
            "transaction_type": item.get("transaction_type"),
            "location": item.get("location"),
            "bedrooms": item.get("bedrooms"),
            "area_sqm": item.get("area_sqm"),
            "price": item.get("price"),
            "currency": item.get("currency", "SAR"),
            "description": item.get("description"),
            "url": item.get("url"),
            "verified_details": True
        })

    return cleaned


def clean_darglobal(projects):
    cleaned = []

    for item in projects:
        cleaned.append({
            "source": "DarGlobal",
            "record_type": "project_reference",
            "title": item.get("project_name"),
            "property_type": None,
            "transaction_type": None,
            "location": None,
            "bedrooms": None,
            "area_sqm": None,
            "price": None,
            "currency": None,
            "description": None,
            "url": item.get("url"),
            "verified_details": False
        })

    return cleaned


def main():
    wasalt = load_json(WASALT_FILE)
    darglobal = load_json(DARGLOBAL_FILE)

    combined = clean_wasalt(wasalt) + clean_darglobal(darglobal)

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

    with open(OUTPUT_FILE, "w", encoding="utf-8") as file:
        json.dump(combined, file, indent=4, ensure_ascii=False)

    print("Wasalt records:", len(wasalt))
    print("DarGlobal records:", len(darglobal))
    print("Total records:", len(combined))
    print("Saved to:", OUTPUT_FILE)


if __name__ == "__main__":
    main()

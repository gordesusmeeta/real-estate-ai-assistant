
import json
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent

WASALT_FILE = ROOT_DIR / "data" / "raw" / "wasalt_properties.json"
DARGLOBAL_FILE = ROOT_DIR / "data" / "raw" / "darglobal_projects.json"
OUTPUT_FILE = ROOT_DIR / "data" / "processed" / "real_estate_data.json"


def load_json(file_path):
    if not file_path.exists():
        print(f"File not found: {file_path}")
        return []

    with open(file_path, "r", encoding="utf-8") as file:
        return json.load(file)


def clean_wasalt(records):
    cleaned = []

    for item in records:
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
            "currency": item.get("currency"),
            "description": item.get("description"),
            "url": item.get("url"),
            "verified_details": True
        })

    return cleaned


def clean_darglobal(records):
    cleaned = []

    for item in records:
        cleaned.append({
            "source": "DarGlobal",
            "record_type": item.get("record_type"),
            "title": item.get("project_name"),
            "property_type": item.get("category"),
            "transaction_type": None,
            "location": item.get("location"),
            "bedrooms": None,
            "area_sqm": None,
            "price": None,
            "currency": None,
            "description": (
                "Official DarGlobal project or property category reference. "
                "Detailed property information could not be extracted."
            ),
            "url": item.get("url"),
            "verified_details": False
        })

    return cleaned


def main():
    print("Loading raw datasets...")

    wasalt_records = load_json(WASALT_FILE)
    darglobal_records = load_json(DARGLOBAL_FILE)

    wasalt_cleaned = clean_wasalt(wasalt_records)
    darglobal_cleaned = clean_darglobal(darglobal_records)

    all_records = wasalt_cleaned + darglobal_cleaned

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

    with open(OUTPUT_FILE, "w", encoding="utf-8") as file:
        json.dump(all_records, file, indent=4, ensure_ascii=False)

    print("\n========== DATA CLEANING SUMMARY ==========")
    print("Wasalt property records:", len(wasalt_cleaned))
    print("DarGlobal records:", len(darglobal_cleaned))
    print("Total records:", len(all_records))
    print(
        "Records with verified property details:",
        sum(1 for r in all_records if r["verified_details"])
    )
    print(
        "DarGlobal references:",
        sum(1 for r in all_records if r["source"] == "DarGlobal")
    )
    print("\nSaved to:", OUTPUT_FILE)


if __name__ == "__main__":
    main()


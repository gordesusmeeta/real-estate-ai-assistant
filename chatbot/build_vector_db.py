
import json
from pathlib import Path

from langchain_core.documents import Document
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma

DATA_FILE = Path("data/processed/real_estate_data.json")
DB_DIRECTORY = "embeddings/chroma_db"


def load_data():
    with open(DATA_FILE, "r", encoding="utf-8") as file:
        return json.load(file)


def create_documents(records):
    documents = []

    for item in records:
        if not item.get("verified_details"):
            continue

        content = f"""
        Source: {item.get('source')}
        Property: {item.get('title')}
        Type: {item.get('property_type')}
        Transaction: {item.get('transaction_type')}
        Location: {item.get('location')}
        Bedrooms: {item.get('bedrooms')}
        Area: {item.get('area_sqm')} SQM
        Price: {item.get('price')} {item.get('currency')}
        Description: {item.get('description')}
        Source URL: {item.get('url')}
        """

        documents.append(
            Document(
                page_content=content,
                metadata={
                    "source": item.get("source"),
                    "url": item.get("url"),
                    "title": item.get("title"),
                    "verified_details": True
                }
            )
        )

    return documents


def main():
    records = load_data()
    documents = create_documents(records)

    if not documents:
        print("No verified property records found.")
        return

    print("Documents to embed:", len(documents))

    print("Loading embedding model...")

    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )

    print("Creating ChromaDB...")

    vector_db = Chroma.from_documents(
        documents=documents,
        embedding=embeddings,
        persist_directory=DB_DIRECTORY,
        collection_name="real_estate_properties"
    )

    print("Vector database created successfully!")
    print("Documents stored:", vector_db._collection.count())


if __name__ == "__main__":
    main()

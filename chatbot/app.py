

import os
import json
from pathlib import Path

import streamlit as st
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

# --------------------------------------------------
# PATHS AND CONFIGURATION
# --------------------------------------------------

ROOT_DIR = Path(__file__).resolve().parent.parent
DATA_FILE = ROOT_DIR / "data" / "processed" / "real_estate_data.json"

load_dotenv(ROOT_DIR / ".env")
API_KEY = os.getenv("OPENROUTER_API_KEY")

st.set_page_config(
    page_title="Real Estate AI Assistant",
    page_icon="🏡",
    layout="centered"
)

st.title("🏡 Real Estate AI Assistant")
st.caption(
    "Ask questions about property listings and projects from "
    "Wasalt and DarGlobal."
)

# --------------------------------------------------
# VALIDATE CONFIGURATION
# --------------------------------------------------

if not API_KEY:
    st.error("OpenRouter API key not found. Check your environment variable.")
    st.stop()

if not DATA_FILE.exists():
    st.error("Property dataset not found. Run the data cleaner first.")
    st.stop()


# --------------------------------------------------
# LOAD DATA
# --------------------------------------------------

@st.cache_data
def load_property_data():
    with open(DATA_FILE, "r", encoding="utf-8") as file:
        return json.load(file)


@st.cache_resource
def load_llm():
    return ChatOpenAI(
        model="openrouter/free",
        openai_api_key=API_KEY,
        openai_api_base="https://openrouter.ai/api/v1",
        temperature=0.2
    )


try:
    records = load_property_data()
    llm = load_llm()
except Exception as error:
    st.error(f"Initialization failed: {error}")
    st.stop()


# --------------------------------------------------
# PREPARE KNOWLEDGE CONTEXT
# --------------------------------------------------

def get_property_context():
    context_parts = []

    for index, item in enumerate(records, start=1):

        source = item.get("source", "Unknown")
        record_type = item.get("record_type", "Unknown")
        verified = item.get("verified_details", False)

        if source == "Wasalt" and verified:
            context = f"""
SOURCE ID: {index}
SOURCE: Wasalt
RECORD TYPE: Property Listing
DETAILS VERIFIED: Yes

Title: {item.get('title')}
Property Type: {item.get('property_type')}
Transaction Type: {item.get('transaction_type')}
Location: {item.get('location')}
Bedrooms: {item.get('bedrooms')}
Area: {item.get('area_sqm')} SQM
Price: {item.get('price')} {item.get('currency')}
Description: {item.get('description')}
URL: {item.get('url')}
"""

        elif source == "DarGlobal":
            context = f"""
SOURCE ID: {index}
SOURCE: DarGlobal
RECORD TYPE: {record_type}
DETAILS VERIFIED: No

Project or Category Name: {item.get('title')}
Category: {item.get('property_type')}
Location: {item.get('location')}
Description: {item.get('description')}
Official URL: {item.get('url')}

IMPORTANT: This is an official sitemap reference only.
Detailed property information was not extracted.
Do not assume prices, amenities, availability, or specifications.
"""

        else:
            continue

        context_parts.append(context)

    return "\n".join(context_parts)


property_context = get_property_context()


# --------------------------------------------------
# GENERATE ANSWER
# --------------------------------------------------

def generate_answer(question):

    prompt = f"""
You are a helpful Real Estate AI Assistant.

You have access to information from two sources:
1. Wasalt property listings.
2. DarGlobal project and category references.

Use ONLY the information provided in the dataset below.

STRICT RULES:

1. Never invent property prices, locations, areas, bedrooms,
   amenities, availability, or other specifications.

2. Wasalt records marked DETAILS VERIFIED: Yes can be used
   to answer property-specific questions.

3. DarGlobal records are official project or category references.
   They are NOT verified property descriptions.

4. You may use DarGlobal records to identify project names,
   category names, and any location information explicitly
   provided in the record.

5. If a user asks for detailed information about a DarGlobal
   project that is not present in the dataset, explain that
   the project is listed in the official sitemap but detailed
   information could not be retrieved.

6. Do not confuse property category pages with individual
   property listings.

7. If information is unavailable, clearly say so.

8. Keep answers clear, concise, and useful.

9. When relevant, mention the source name and provide its URL.

DATASET:

{property_context}

USER QUESTION:
{question}

ANSWER:
"""

    response = llm.invoke(prompt)

    if isinstance(response.content, str):
        return response.content

    return str(response.content)


# --------------------------------------------------
# CHAT INTERFACE
# --------------------------------------------------

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

question = st.chat_input(
    "Ask about properties or projects..."
)

if question:

    st.session_state.messages.append({
        "role": "user",
        "content": question
    })

    with st.chat_message("user"):
        st.markdown(question)

    with st.chat_message("assistant"):
        with st.spinner("Searching property information..."):

            try:
                answer = generate_answer(question)
                st.markdown(answer)

                st.session_state.messages.append({
                    "role": "assistant",
                    "content": answer
                })

            except Exception as error:
                st.error(f"Unable to generate an answer: {error}")


# --------------------------------------------------
# SIDEBAR
# --------------------------------------------------

with st.sidebar:
    st.header("Dataset Information")

    wasalt_count = sum(
        1 for item in records
        if item.get("source") == "Wasalt"
    )

    darglobal_count = sum(
        1 for item in records
        if item.get("source") == "DarGlobal"
    )

    verified_count = sum(
        1 for item in records
        if item.get("verified_details") is True
    )

    st.metric("Total Records", len(records))
    st.metric("Wasalt Records", wasalt_count)
    st.metric("DarGlobal References", darglobal_count)
    st.metric("Verified Property Records", verified_count)

    st.divider()

    st.subheader("Data Sources")

    with st.expander("Wasalt sources"):
        for item in records:
            if item.get("source") == "Wasalt" and item.get("url"):
                st.markdown(
                    f"- [{item.get('title', 'Property listing')}]"
                    f"({item['url']})"
                )

    with st.expander("DarGlobal sources"):
        for item in records:
            if item.get("source") == "DarGlobal" and item.get("url"):
                st.markdown(
                    f"- [{item.get('title', 'Project reference')}]"
                    f"({item['url']})"
                )

    st.divider()

    if st.button("Clear Chat", use_container_width=True):
        st.session_state.messages = []
        st.rerun()


import os
import json
from pathlib import Path

import streamlit as st
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI


# Project paths
ROOT_DIR = Path(__file__).resolve().parent.parent
DATA_FILE = ROOT_DIR / "data" / "processed" / "real_estate_data.json"

# Load API key
load_dotenv(ROOT_DIR / ".env")
API_KEY = os.getenv("OPENROUTER_API_KEY")


# Streamlit configuration
st.set_page_config(
    page_title="Real Estate AI Assistant",
    page_icon="🏡",
    layout="centered"
)

st.title("🏡 Real Estate AI Assistant")
st.caption("Ask questions about available property listings.")


# Validate configuration
if not API_KEY:
    st.error("OpenRouter API key not found. Check your environment variable.")
    st.stop()

if not DATA_FILE.exists():
    st.error("Property data file not found.")
    st.stop()


# Load verified property records
@st.cache_data
def load_property_data():
    with open(DATA_FILE, "r", encoding="utf-8") as file:
        records = json.load(file)

    return [
        record for record in records
        if record.get("verified_details") is True
    ]


# Connect to OpenRouter
@st.cache_resource
def load_llm():
    return ChatOpenAI(
        model="openrouter/free",
        openai_api_key=API_KEY,
        openai_api_base="https://openrouter.ai/api/v1",
        temperature=0.2
    )


try:
    properties = load_property_data()
    llm = load_llm()
except Exception as error:
    st.error(f"Initialization failed: {error}")
    st.stop()


# Prepare property context
def get_property_context():
    context_parts = []
    sources = []

    for index, property_data in enumerate(properties, start=1):
        context_parts.append(
            f"""
PROPERTY {index}

Title: {property_data.get('title')}
Property Type: {property_data.get('property_type')}
Transaction Type: {property_data.get('transaction_type')}
Location: {property_data.get('location')}
Bedrooms: {property_data.get('bedrooms')}
Area: {property_data.get('area_sqm')} SQM
Price: {property_data.get('price')} {property_data.get('currency')}
Description: {property_data.get('description')}
"""
        )

        url = property_data.get("url")
        title = property_data.get("title", "Property listing")

        if url:
            sources.append((title, url))

    return "\n".join(context_parts), sources


# Generate grounded response
def generate_answer(question):
    if not properties:
        return "No verified property records are currently available.", []

    context, sources = get_property_context()

    prompt = f"""
You are a helpful real estate assistant.

Answer the user's question using ONLY the verified property
information provided below.

Rules:
1. Never invent prices, locations, amenities, or property details.
2. If information is missing, clearly say it is not available.
3. Preserve the original currency and measurement units.
4. Compare properties only using the supplied information.
5. For cheapest or most expensive questions, compare the
   available prices when their currencies are the same.
6. Do not treat missing information as a confirmed fact.
7. Keep answers clear and concise.

VERIFIED PROPERTY DATA:
{context}

USER QUESTION:
{question}

ANSWER:
"""

    response = llm.invoke(prompt)

    return response.content, sources


# Chat interface
if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

        if message.get("sources"):
            st.markdown("**Sources:**")
            for title, url in message["sources"]:
                st.markdown(f"- [{title}]({url})")


question = st.chat_input("Ask about properties, prices, or locations...")

if question:
    st.session_state.messages.append({
        "role": "user",
        "content": question
    })

    with st.chat_message("user"):
        st.markdown(question)

    with st.chat_message("assistant"):
        with st.spinner("Searching property listings..."):
            try:
                answer, sources = generate_answer(question)
                st.markdown(answer)

                if sources:
                    st.markdown("**Sources:**")
                    for title, url in sources:
                        st.markdown(f"- [{title}]({url})")

            except Exception as error:
                answer = f"Sorry, something went wrong: {error}"
                sources = []
                st.error(answer)

    st.session_state.messages.append({
        "role": "assistant",
        "content": answer,
        "sources": sources
    })


# Sidebar
with st.sidebar:
    st.subheader("About this assistant")
    st.write(
        "AI-powered property assistant using verified property "
        "data and OpenRouter."
    )

    st.write("**Current database:**")
    st.write(f"{len(properties)} verified property records")

    if st.button("Clear chat"):
        st.session_state.messages = []
        st.rerun()

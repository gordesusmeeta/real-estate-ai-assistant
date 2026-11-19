
import os
from pathlib import Path

import streamlit as st
from dotenv import load_dotenv
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_openai import ChatOpenAI


# Project paths
ROOT_DIR = Path(__file__).resolve().parent.parent
DB_DIRECTORY = ROOT_DIR / "embeddings" / "chroma_db"

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

if not API_KEY:
    st.error("OpenRouter API key not found. Please check your .env file.")
    st.stop()

if not DB_DIRECTORY.exists():
    st.error("Vector database not found. Please build ChromaDB first.")
    st.stop()


# Load embedding model and vector database
@st.cache_resource
def load_vector_database():
    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )

    database = Chroma(
        collection_name="real_estate_properties",
        persist_directory=str(DB_DIRECTORY),
        embedding_function=embeddings
    )

    return database


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
    vector_db = load_vector_database()
    llm = load_llm()
except Exception as error:
    st.error(f"Initialization failed: {error}")
    st.stop()


# Retrieve relevant properties
def get_property_context(question):
    documents = vector_db.similarity_search(question, k=3)

    if not documents:
        return "", []

    context_parts = []
    sources = []

    for document in documents:
        context_parts.append(document.page_content)

        url = document.metadata.get("url")
        title = document.metadata.get("title", "Property listing")

        if url:
            sources.append((title, url))

    return "\n\n".join(context_parts), sources


# Generate grounded response
def generate_answer(question):
    context, sources = get_property_context(question)

    if not context:
        return (
            "I couldn't find any verified property information "
            "in the current database. Please try another question."
        ), []

    prompt = f"""
You are a helpful real estate assistant.

Answer the user's question using ONLY the property information
provided in the context below.

Rules:
1. Do not invent prices, locations, amenities, or property details.
2. If information is missing, clearly say it is not available.
3. Mention the currency and measurement units exactly as provided.
4. Compare properties only when the context supports the comparison.
5. Keep answers clear and concise.

PROPERTY CONTEXT:
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
    st.write("AI-powered property search using retrieval-augmented generation.")

    st.write("**Current database:**")
    st.write(f"{vector_db._collection.count()} verified property records")

    if st.button("Clear chat"):
        st.session_state.messages = []
        st.rerun()

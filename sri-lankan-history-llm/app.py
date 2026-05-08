"""
app.py
------
Streamlit chat app. On every user question:
1. Embed the question.
2. Pull the top-k most similar chunks from Chroma.
3. Send them, plus the system prompt and chat history, to Gemini.
4. Stream the answer back.

Run locally:
    streamlit run app.py

Deploy free: push this repo to GitHub, then connect at https://streamlit.io/cloud
and add GEMINI_API_KEY in the app's Secrets settings.
"""

from __future__ import annotations

import os
from pathlib import Path

import chromadb
import google.generativeai as genai
import streamlit as st
from chromadb.utils import embedding_functions
from dotenv import load_dotenv

# ---- config ----
# Resolve paths relative to this file so they work whether the app is run from
# the script's folder (local) or the repo root (Streamlit Cloud).
HERE = Path(__file__).parent
DB_DIR = str(HERE / "vectorstore")
COLLECTION_NAME = "sri_lankan_history"
EMBED_MODEL = "all-MiniLM-L6-v2"
GEMINI_MODEL = "gemini-2.5-flash"   # free tier, fast
TOP_K = 5
SYSTEM_PROMPT_PATH = HERE / "system_prompt.txt"

load_dotenv()

# Streamlit Cloud puts secrets in st.secrets; locally we use .env
API_KEY = os.getenv("GEMINI_API_KEY")
if not API_KEY:
    try:
        API_KEY = st.secrets.get("GEMINI_API_KEY", None)
    except Exception:
        API_KEY = None
if not API_KEY:
    st.error("Missing GEMINI_API_KEY. Add it to .env locally or to Secrets on Streamlit Cloud.")
    st.stop()

genai.configure(api_key=API_KEY)


@st.cache_resource(show_spinner="Loading vector store...")
def get_collection():
    embed_fn = embedding_functions.SentenceTransformerEmbeddingFunction(model_name=EMBED_MODEL)
    client = chromadb.PersistentClient(path=DB_DIR)
    return client.get_collection(name=COLLECTION_NAME, embedding_function=embed_fn)


@st.cache_data
def load_system_prompt() -> str:
    if SYSTEM_PROMPT_PATH.exists():
        return SYSTEM_PROMPT_PATH.read_text(encoding="utf-8")
    return "You are a helpful Sri Lankan history assistant."


def retrieve(query: str, k: int = TOP_K) -> list[dict]:
    collection = get_collection()
    res = collection.query(query_texts=[query], n_results=k)
    docs = res["documents"][0]
    metas = res["metadatas"][0]
    return [{"text": d, "source": m.get("source", "unknown")} for d, m in zip(docs, metas)]


def build_prompt(user_question: str, history: list[dict]) -> str:
    chunks = retrieve(user_question)
    context_block = "\n\n".join(
        f"[Source: {c['source']}]\n{c['text']}" for c in chunks
    )

    history_block = ""
    for turn in history[-6:]:   # keep last 3 exchanges
        role = "User" if turn["role"] == "user" else "Historian"
        history_block += f"{role}: {turn['content']}\n"

    return (
        f"{load_system_prompt()}\n\n"
        f"CONTEXT:\n{context_block}\n\n"
        f"PRIOR CONVERSATION:\n{history_block}\n"
        f"User: {user_question}\n"
        f"Historian:"
    )


# ---- UI ----
st.set_page_config(page_title="Sri Lankan History LLM", page_icon=None, layout="centered")
st.title("Sri Lankan History")
st.caption("Ask about any period from the Anuradhapura kingdom to the modern era.")

if "messages" not in st.session_state:
    st.session_state.messages = []

with st.sidebar:
    st.subheader("About")
    st.write(
        "This assistant answers from a curated set of sources: the Mahavamsa, "
        "Culavamsa, Wikipedia, and academic papers you've ingested. Answers cite "
        "the source they came from."
    )
    if st.button("Clear chat"):
        st.session_state.messages = []
        st.rerun()

# Replay history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Input
if user_input := st.chat_input("e.g. Who was Parakramabahu the Great?"):
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    with st.chat_message("assistant"):
        placeholder = st.empty()
        prompt = build_prompt(user_input, st.session_state.messages[:-1])
        model = genai.GenerativeModel(GEMINI_MODEL)
        try:
            response = model.generate_content(prompt, stream=True)
            answer = ""
            for chunk in response:
                if chunk.text:
                    answer += chunk.text
                    placeholder.markdown(answer + "...")
            placeholder.markdown(answer)
        except Exception as exc:
            answer = f"Error talking to Gemini: {exc}"
            placeholder.error(answer)

    st.session_state.messages.append({"role": "assistant", "content": answer})

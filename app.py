import os

import httpx
import streamlit as st
from dotenv import load_dotenv
from google.genai import errors
from pypdf import PdfReader

from gemini_client import MANUAL_PATH, ask, build_index, get_client

load_dotenv()

st.set_page_config(page_title="DHF Blender Manual Assistant", page_icon="🔧", layout="centered")

# Let each paragraph pick its own direction so Hebrew renders RTL and English LTR.
st.markdown(
    """
    <style>
    [data-testid="stChatMessageContent"] p,
    [data-testid="stChatMessageContent"] li,
    [data-testid="stChatInput"] textarea {
        unicode-bidi: plaintext;
        text-align: start;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


@st.cache_data(show_spinner=False)
def page_count() -> int:
    return len(PdfReader(MANUAL_PATH).pages)


@st.cache_resource(show_spinner=False)
def client_for(api_key: str):
    return get_client(api_key)


@st.cache_resource(show_spinner=False)
def index_for(api_key: str):
    return build_index(client_for(api_key))


model = os.getenv("GEMINI_MODEL", "gemini-3.8-flash")
fallback_models = [
    m.strip() for m in os.getenv("GEMINI_FALLBACK_MODEL", "gemini-3.7-flash,gemini-3.6-flash,gemini-3.5-flash,gemini-3.1-flash-lite").split(",") if m.strip()
]
models = [model, *fallback_models]
api_key = os.getenv("GEMINI_API_KEY", "").strip()

with st.sidebar:
    st.header("📘 Manual")
    st.write(f"**{MANUAL_PATH.stem}**")
    st.caption(f"{page_count()} pages · model: `{model}`")
    st.caption(f"Fallbacks: {', '.join(f'`{m}`' for m in fallback_models)}")

    if not api_key:
        api_key = st.text_input(
            "Gemini API key",
            type="password",
            help="Get a key at https://aistudio.google.com/apikey, or set GEMINI_API_KEY in a .env file.",
        ).strip()

    if st.button("🗑️ New chat", width="stretch"):
        st.session_state.messages = []
        st.rerun()

    st.divider()
    st.caption("Answers are based only on the manual and include page references. Ask in English or Hebrew.")

st.title("🔧 DHF Blender Manual Assistant")

if not api_key:
    st.error("No Gemini API key found. Add GEMINI_API_KEY to a .env file or enter it in the sidebar.")
    st.stop()

try:
    with st.spinner("Indexing the manual (one-time, may take several minutes on the free tier)..."):
        index = index_for(api_key)
except errors.APIError as e:
    st.error(f"Could not index the manual with Gemini: {e.message or e}")
    st.stop()
except httpx.TimeoutException:
    st.error("Timed out indexing the manual. Please refresh to try again.")
    st.stop()

if "messages" not in st.session_state:
    st.session_state.messages = []

if not st.session_state.messages:
    st.info("Ask anything about the DHF Blender, e.g. *How do I flush the daytanks?* or *איך מבצעים שטיפה לתא הדגימה?*")

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if question := st.chat_input("Ask a question about the manual..."):
    with st.chat_message("user"):
        st.markdown(question)

    with st.chat_message("assistant"):
        try:
            answer = st.write_stream(
                ask(client_for(api_key), models, index, st.session_state.messages, question)
            )
        except errors.APIError as e:
            if e.code == 429:
                st.error("Gemini quota or rate limit reached. Please wait a moment and try again.")
            elif e.code == 503:
                st.error("Gemini is busy right now (high demand). Please try again in a moment.")
            else:
                st.error(f"Gemini error: {e.message or e}")
            st.stop()
        except httpx.TimeoutException:
            st.error("Gemini took too long to respond. Please try again.")
            st.stop()

    st.session_state.messages.append({"role": "user", "content": question})
    st.session_state.messages.append({"role": "assistant", "content": answer})

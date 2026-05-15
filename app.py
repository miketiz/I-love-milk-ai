"""Streamlit app for Demi RAG Chatbot."""

import os

import streamlit as st
from dotenv import load_dotenv
from google import genai

from rag_engine import RAGEngine

load_dotenv(dotenv_path=".env", override=True)

st.set_page_config(page_title="Demi RAG Chatbot", page_icon="🥛")


def get_api_key() -> str | None:
    api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
    if api_key:
        return api_key

    try:
        return st.secrets.get("GOOGLE_API_KEY") or st.secrets.get("GEMINI_API_KEY")
    except Exception:  # noqa: BLE001
        return None


api_key = get_api_key()
if not api_key:
    raise ValueError("GOOGLE_API_KEY (or GEMINI_API_KEY) not found in environment or Streamlit secrets")

client = genai.Client(api_key=api_key)
MODEL = "gemini-2.5-flash"


@st.cache_resource
def load_rag() -> RAGEngine:
    return RAGEngine("knowledge/milklab_kb.txt")


rag = load_rag()

st.title("🥛 Demi ผู้ช่วย AI ของ MilkLab°")
st.caption("ถามเรื่องเมนู เวลาเปิด หรือข้อมูลร้านได้เลย")

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

if prompt := st.chat_input("ถามอะไรเกี่ยวกับร้านได้เลย..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)

    context_chunks = rag.search(prompt, top_k=3)
    context = "\n---\n".join(context_chunks)

    full_prompt = f"""คุณคือ Demi ผู้ช่วย AI ของร้าน MilkLab°
ตอบเฉพาะจากข้อมูลด้านล่าง ถ้าไม่พบข้อมูลให้บอกว่าไม่ทราบ อย่าแต่งข้อมูลเอง

ข้อมูลร้าน:
{context}

คำถาม: {prompt}
"""

    response = client.models.generate_content(model=MODEL, contents=full_prompt)
    answer = (response.text or "").strip()

    st.session_state.messages.append({"role": "assistant", "content": answer})
    with st.chat_message("assistant"):
        st.write(answer)

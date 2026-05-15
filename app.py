"""Streamlit app for Demi RAG Chatbot."""

import os

import streamlit as st
from dotenv import load_dotenv
from google import genai

from rag_engine import RAGEngine

load_dotenv(dotenv_path=".env", override=True)

st.set_page_config(page_title="Demi RAG Chatbot", page_icon="🥛")


def get_api_key() -> str | None:
    # Check environment variables (HF Spaces, Docker, local .env)
    api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
    if api_key:
        return api_key

    # Check Streamlit secrets (local development)
    try:
        return st.secrets.get("GOOGLE_API_KEY") or st.secrets.get("GEMINI_API_KEY")
    except Exception:  # noqa: BLE001
        pass
    
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

FALLBACK_MESSAGE = (
    "ขอโทษครับ Demi ยังไม่พบข้อมูลใน knowledge base สำหรับคำถามนี้ "
    "ลองถามใหม่เป็นเรื่องเมนู เวลาเปิดร้าน วิธีสั่ง หรือส่วนผสมของเมนูได้เลย"
)
FALLBACK_DISTANCE_THRESHOLD = 0.8

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

    search_results = rag.search_with_scores(prompt, top_k=4)
    if not search_results or search_results[0].score > FALLBACK_DISTANCE_THRESHOLD:
        st.session_state.messages.append({"role": "assistant", "content": FALLBACK_MESSAGE})
        with st.chat_message("assistant"):
            st.write(FALLBACK_MESSAGE)
        st.stop()

    context_chunks = [result.chunk for result in search_results]
    context = "\n---\n".join(context_chunks)

    full_prompt = f"""คุณคือ Demi ผู้ช่วย AI ของร้าน MilkLab°
ตอบเฉพาะจากข้อมูลด้านล่าง ถ้าไม่พบข้อมูลให้บอกว่าไม่ทราบ อย่าแต่งข้อมูลเอง
ถ้าข้อมูลไม่ครบ ให้ตอบเฉพาะส่วนที่มั่นใจ และบอกว่าตรวจสอบกับร้านเพิ่มเติมได้

ข้อมูลร้าน:
{context}

คำถาม: {prompt}
"""

    response = client.models.generate_content(model=MODEL, contents=full_prompt)
    answer = (response.text or "").strip()

    st.session_state.messages.append({"role": "assistant", "content": answer})
    with st.chat_message("assistant"):
        st.write(answer)

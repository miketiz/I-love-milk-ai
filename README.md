---
title: Milklab Demi
emoji: 🚀
colorFrom: red
colorTo: red
sdk: docker
app_port: 8501
tags:
- streamlit
pinned: false
short_description: Streamlit template space
---

# I-love-milk-ai

Instagram caption generator for I Love Milk Cafe using Google Gemini AI.

## Session 3 & 4: Demi AI Agent with Q&A & Sales Logging

This repository includes:
1. **Agent Harness** (`agent_harness.py`) - Dual-mode AI agent that can:
   - Log sales to Google Sheets
   - Answer customer questions about the store
2. **RAG Chatbot** (`app.py`) - Streamlit web UI for Demi
3. **Sales Logger** (`sales_logger.py`, `sheets_client.py`) - Log sales to Google Sheets
4. **Morning Report** (`morning_report.py`) - Daily sales summary via Telegram

### Key Files

- `agent_harness.py` - Main agent that routes between sales logging and Q&A
- `agent_tools.py` - Tool definitions (log_sale, answer_question)
- `rag_engine.py` - Retrieval-Augmented Generation for knowledge base search
- `app.py` - Streamlit chat UI for Demi
- `knowledge/milklab_kb.txt` - Store knowledge base (menus, hours, FAQ)
- `sales_logger.py` - CLI for logging individual sales
- `morning_report.py` - Daily Telegram sales summary
- `sheets_client.py` - Google Sheets API client
- `.github/workflows/morning-report.yml` - GitHub Actions scheduled daily report

### Quick Start

#### 1. Run the Agent (CLI mode)

Install dependencies:

```powershell
python -m pip install -r requirements.txt
```

Set `GOOGLE_API_KEY` in `.env`, then run:

```powershell
python agent_harness.py
```

The agent will prompt for your input. Try:

**Sales Command:**
```
คุณ: บันทึกยอดขายลาเต้น้ำผึ้ง 5 แก้ว ราคา 65 บาท
Demi: ✅ บันทึกสำเร็จ...
```

**Question (Q&A):**
```
คุณ: ลาเต้มีน้ำตาลไหม
Demi: [Searches KB] ใช่ ลาเต้มีน้ำตาล แต่คุณสามารถสั่งไม่หวานได้...
```

#### 2. Run the Web Chatbot (Streamlit)

```powershell
streamlit run app.py
```

Ask questions like:
- ในลาเต้มีน้ำตาลไหม
- ร้านเปิดถึงกี่โมง
- มีเมนูอะไรบ้าง

#### 3. Log Sales via CLI

```powershell
python sales_logger.py "ลาเต้น้ำผึ้ง:5:65"
```

This appends to your Google Sheets.

#### 4. Deploy Chatbot to HuggingFace Spaces

1. Go to HuggingFace Spaces and create a new Space.
2. Choose SDK: `Streamlit`.
3. Connect this GitHub repo or upload the files.
4. Add a secret named `GOOGLE_API_KEY` in Spaces settings.
5. Wait for the build to finish.

### Agent Capabilities

**Mode 1: Sales Logging**
- Format: `บันทึกยอดขาย[เมนู] [จำนวน] [หน่วย] ราคา [ราคา] บาท`
- Examples:
  - `บันทึกยอดขายลาเต้น้ำผึ้ง 5 แก้ว ราคา 65 บาท`
  - `ขายคัฟเฟ่โม 3 ชิ้น ละ 45 บาท`
- Result: Logged to Google Sheets

**Mode 2: Q&A about Store**
- Format: Any natural language question
- Examples:
  - `ลาเต้มีน้ำตาลไหม`
  - `ร้านเปิดกี่โมง`
  - `มีเมนูอะไรไม่มีแคฟเฟอีน`
- Result: Answers from knowledge base

The agent intelligently routes questions to the right tool using LLM + RAG.

### Architecture

```
User Input
    ↓
Agent Harness (LLM Router)
    ├→ Direct Sales Pattern Match? → log_sale tool
    ├→ LLM recognizes Q&A? → answer_question tool
    │   └→ RAG Engine searches KB
    │   └→ LLM generates answer from context
    └→ Unknown? → Friendly fallback message
```

## Requirements

- Python 3.10 or newer
- A Google Gemini API key
- Google Sheets (optional, for sales logging)
- Telegram Bot (optional, for daily reports)

## Environment variables

Create a `.env` file in the project root:

```env
GOOGLE_API_KEY=your_api_key_here
GOOGLE_SHEETS_ID=your_sheet_id
GOOGLE_SERVICE_ACCOUNT_JSON={"type":"service_account",...}
TELEGRAM_BOT_TOKEN=your_bot_token
TELEGRAM_CHAT_ID=your_chat_id
```

## Install dependencies

```powershell
python -m pip install -r requirements.txt
```

If you are using a virtual environment, activate it first and run the same command inside that environment.

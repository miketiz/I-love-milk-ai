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

## Session 3: Demi RAG Chatbot

This repository now includes a simple RAG chatbot for MilkLab°.

Files:

- `knowledge/milklab_kb.txt` - source knowledge base for the store
- `rag_engine.py` - chunk, embed, and search the knowledge base
- `app.py` - Streamlit chat UI for Demi

### Deploy to HuggingFace Spaces

1. Go to HuggingFace Spaces and create a new Space.
2. Choose SDK: `Streamlit`.
3. Connect this GitHub repo or upload the files.
4. Add a secret named `GOOGLE_API_KEY` in Spaces settings.
5. Wait for the build to finish, then open the Space URL.

The app reads `GOOGLE_API_KEY` from environment variables or Streamlit secrets.

### Run locally

Install dependencies:

```powershell
python -m pip install -r requirements.txt
```

Set `GOOGLE_API_KEY` in `.env`, then run:

```powershell
streamlit run app.py
```

Ask questions like:

- ในลาเต้มีน้ำตาลไหม
- ร้านเปิดถึงกี่โมง
- มีเมนูอะไรบ้าง

## Requirements

If you want to use this source code, you need:

- Python 3.10 or newer
- A Google Gemini API key
- The Python packages listed below

## Install dependencies

Install the required packages in your active Python environment:

```powershell
python -m pip install python-dotenv google-generativeai
```

If you are using a virtual environment, activate it first and run the same command inside that environment.

## Environment variables

Create a file named `.env` in the project root and add your Gemini API key:

```env
GOOGLE_API_KEY=your_api_key_here
```

## How to run

```powershell
python caption.py
```

## What this code does

The script loads `GOOGLE_API_KEY` from `.env`, connects to Gemini, and generates three Instagram caption styles for a menu item:

- cute
- minimal
- gen_z

## Notes for reuse

If someone copies this source code into another project, they must still:

- install the same Python dependencies
- provide a valid `GOOGLE_API_KEY`
- make sure the Python interpreter matches the environment where the packages were installed

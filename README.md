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

FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    git \
    libjpeg-dev \
    libpng-dev \
    libopenjp2-7-dev \
    libtiff-dev \
    libwebp-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt ./
COPY app.py ./
COPY rag_engine.py ./
COPY sitecustomize.py ./
COPY knowledge/ ./knowledge/
COPY src/ ./src/
COPY .streamlit/ .streamlit/

RUN pip3 install --upgrade pip setuptools wheel && \
    pip3 install -r requirements.txt --no-cache-dir

ENV PYTHONPATH=/app:${PYTHONPATH}
ENV STREAMLIT_SERVER_FILE_WATCHER_TYPE=none
ENV STREAMLIT_SERVER_FILE_WATCHER_ENABLED=false
ENV STREAMLIT_LOGGER_LEVEL=warning
ENV HF_HUB_OFFLINE=1
ENV TRANSFORMERS_OFFLINE=1
ENV TRANSFORMERS_CACHE=/tmp/transformers_cache
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

EXPOSE 8501

HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health

CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]

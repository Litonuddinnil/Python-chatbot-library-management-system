FROM python:3.10-slim

WORKDIR /app

# System deps needed by faiss / torch / sentence-transformers
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# HF Spaces expects the app to listen on 7860
ENV PORT=7860
EXPOSE 7860

CMD ["python", "app.py"]
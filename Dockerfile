FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY app /app/app
COPY scripts /app/scripts
COPY data /app/data

ENV CHROMA_PERSIST_DIR=/app/chroma_data
ENV LOG_DIR=/app/logs
ENV PYTHONUNBUFFERED=1

EXPOSE 8000

CMD ["bash", "-lc", "python -m scripts.ingest && uvicorn app.main:app --host 0.0.0.0 --port 8000"]


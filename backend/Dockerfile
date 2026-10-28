# Production Dockerfile for F1 Race Intelligence Backend API
FROM python:3.13-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy dependency requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application and dataset
COPY app/ ./app/
COPY data/ ./data/

ENV PYTHONUNBUFFERED=1
ENV DATABASE_URL=sqlite:///./data/f1_data.db
ENV API_HOST=0.0.0.0
ENV API_PORT=8000

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

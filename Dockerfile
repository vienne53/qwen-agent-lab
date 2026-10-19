FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -U pip && pip install --no-cache-dir -r requirements.txt

COPY app.py .
COPY apps/ apps/
COPY kb/ kb/

ENV PYTHONUNBUFFERED=1
EXPOSE 7860

CMD ["python", "app.py"]

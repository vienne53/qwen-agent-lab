FROM python:3.12-slim

WORKDIR /app

# git：pip 从 GitHub fork 安装 qwen-agent 时需要
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    git \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -U pip \
    && pip install --no-cache-dir -r requirements.txt

COPY app.py agents_factory.py ./
COPY apps/ apps/
COPY ui/ ui/
COPY kb/ kb/

ENV PYTHONUNBUFFERED=1
EXPOSE 7860

CMD ["python", "app.py"]

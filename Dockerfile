FROM python:3.12-slim

WORKDIR /app

ENV PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    GIT_TERMINAL_PROMPT=0

# git：拉取你的 Qwen-Agent fork；build-essential：编译部分依赖
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    git \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# 浅克隆你的 fork（比 pip git+https 在 Render 上更稳）
RUN git clone --depth 1 --branch main \
      https://github.com/vienne53/Qwen-Agent.git /opt/Qwen-Agent \
    && pip install --no-cache-dir -U pip setuptools wheel \
    && pip install --no-cache-dir "/opt/Qwen-Agent[rag,gui]" \
    && pip install --no-cache-dir tqdm soundfile

COPY app.py agents_factory.py ./
COPY apps/ apps/
COPY ui/ ui/
COPY kb/ kb/

EXPOSE 7860
CMD ["python", "app.py"]

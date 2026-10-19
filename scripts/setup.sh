#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."

python3 -m venv .venv
# shellcheck disable=SC1091
source .venv/bin/activate
python -m pip install -U pip
pip install -r requirements.txt

if [[ -n "${DASHSCOPE_API_KEY:-}" ]]; then
  echo "DASHSCOPE_API_KEY detected (len=${#DASHSCOPE_API_KEY})."
else
  echo "请先 export DASHSCOPE_API_KEY=你的密钥，再运行: python app.py"
fi

echo "安装完成。启动: python app.py"

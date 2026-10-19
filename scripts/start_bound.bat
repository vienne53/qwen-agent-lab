@echo off
cd /d D:\qwen-agent-lab
if exist .venv\Scripts\activate.bat call .venv\Scripts\activate.bat
python apps\app_bound_kb.py
pause

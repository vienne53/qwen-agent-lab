@echo off
cd /d "%~dp0.."
if exist .venv\Scripts\activate.bat call .venv\Scripts\activate.bat
if not defined DASHSCOPE_API_KEY (
  for /f "usebackq delims=" %%i in (`powershell -NoProfile -Command "[Environment]::GetEnvironmentVariable('DASHSCOPE_API_KEY','User')"`) do set "DASHSCOPE_API_KEY=%%i"
)
python app.py
pause

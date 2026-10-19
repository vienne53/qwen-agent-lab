# One-shot setup on a new machine (Windows PowerShell)
$ErrorActionPreference = "Stop"
Set-Location (Split-Path $PSScriptRoot -Parent)

if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
    Write-Error "需要先安装 Python 3.10+，并确保 python 在 PATH 中。"
}

if (-not (Test-Path .venv)) {
    python -m venv .venv
}
.\.venv\Scripts\Activate.ps1
python -m pip install -U pip
pip install -r requirements.txt

$key = [Environment]::GetEnvironmentVariable("DASHSCOPE_API_KEY", "User")
if (-not $key) { $key = $env:DASHSCOPE_API_KEY }
if ($key) {
    Write-Host "DASHSCOPE_API_KEY 已检测到（长度 $($key.Length)）。"
} else {
    Write-Host @"
尚未检测到 DASHSCOPE_API_KEY。请任选其一：
  1) 本机用户环境变量（推荐）：
     [Environment]::SetEnvironmentVariable('DASHSCOPE_API_KEY','你的密钥','User')
     然后新开终端。
  2) 当前会话临时：
     `$env:DASHSCOPE_API_KEY = '你的密钥'
"@
}

Write-Host "安装完成。启动："
Write-Host "  python app.py"
Write-Host "  或 scripts\start_app.bat"

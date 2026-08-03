@echo off
chcp 65001 >nul
title 启动后端服务 - FastAPI

echo ========================================
echo   启动后端服务 (FastAPI + Uvicorn)
echo ========================================
echo.

cd /d %~dp0backend

REM 检查 Python 是否安装
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [错误] 未检测到 Python，请先安装 Python 3.8+
    pause
    exit /b 1
)

echo [信息] Python 已就绪
echo [信息] 正在启动后端服务...
echo.
echo [提示] 后端 API 地址: http://localhost:8000
echo [提示] API 文档地址: http://localhost:8000/docs
echo [提示] 按 Ctrl+C 停止服务
echo.

python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

pause

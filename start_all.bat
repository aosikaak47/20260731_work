@echo off
chcp 65001 >nul
title AI智能测试自动化平台 - 一键启动

echo ========================================
echo   AI智能测试自动化平台 - 一键启动
echo ========================================
echo.
echo [1/3] 检查环境依赖...

REM 检查 Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [错误] 未检测到 Python，请先安装 Python 3.8+
    pause
    exit /b 1
)
echo       Python 已就绪

REM 检查 Node.js
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [错误] 未检测到 Node.js，请先安装 Node.js 16+
    pause
    exit /b 1
)
echo       Node.js 已就绪

echo.
echo [2/3] 启动后端服务...
start "后端服务 - FastAPI" cmd /c "cd /d %~dp0backend && python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload"
timeout /t 3 /nobreak >nul

echo [3/3] 启动前端服务...
start "前端服务 - Vue + Vite" cmd /c "cd /d %~dp0frontend && if not exist node_modules (npm install) && npm run dev"

echo.
echo ========================================
echo   服务启动中，请稍候...
echo ========================================
echo.
echo   后端 API:  http://localhost:8000
echo   API 文档:  http://localhost:8000/docs
echo   前端 UI:   http://localhost:5173
echo.
echo   关闭此窗口不会影响已启动的服务
echo   如需停止服务，请关闭对应的命令行窗口
echo ========================================
echo.

REM 等待服务启动后打开浏览器
timeout /t 5 /nobreak >nul
start http://localhost:5173

echo [完成] 服务已启动，浏览器正在打开...
echo.
pause

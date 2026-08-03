@echo off
chcp 65001 >nul
title 启动前端服务 - Vue + Vite

echo ========================================
echo   启动前端服务 (Vue 3 + Vite)
echo ========================================
echo.

cd /d %~dp0frontend

REM 检查 Node.js 是否安装
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [错误] 未检测到 Node.js，请先安装 Node.js 16+
    pause
    exit /b 1
)

echo [信息] Node.js 已就绪

REM 检查 node_modules 是否存在
if not exist "node_modules" (
    echo [提示] 首次运行，正在安装依赖...
    call npm install
    if %errorlevel% neq 0 (
        echo [错误] 依赖安装失败
        pause
        exit /b 1
    )
)

echo [信息] 正在启动前端服务...
echo.
echo [提示] 前端 UI 地址: http://localhost:5173
echo [提示] 按 Ctrl+C 停止服务
echo.

call npm run dev

pause

@echo off
chcp 65001 >nul
title 🚀 股票分析最大效能啟動器

echo.
echo ========================================
echo    🚀 股票分析最大效能啟動器
echo    讓您的電腦發揮最大效能跑數據！
echo ========================================
echo.

REM 設定高效能電源計劃
echo 🔋 正在設定高效能電源計劃...
powercfg -setactive 8c5e7fda-e8bf-4a96-9a85-a6e23a8c635c 2>nul
if %errorlevel% == 0 (
    echo ✅ 高效能電源計劃已啟用
) else (
    echo ⚠️ 無法設定電源計劃（需要管理員權限）
)

echo.
echo 🐍 正在啟動 Python 最大效能模式...
echo.

REM 設定環境變數並執行 Python
set OMP_NUM_THREADS=%NUMBER_OF_PROCESSORS%
set NUMBA_NUM_THREADS=%NUMBER_OF_PROCESSORS%
set MKL_NUM_THREADS=%NUMBER_OF_PROCESSORS%
set PYTHONHASHSEED=0

REM 執行 Python 腳本
".venv\Scripts\python.exe" start_max_performance.py

echo.
echo 🎯 按任意鍵關閉視窗...
pause >nul

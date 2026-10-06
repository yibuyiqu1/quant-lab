@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo ============================================================
echo  运行：Day 1 全部测试（14 项）
echo ============================================================
echo.
if not exist ".venv\Scripts\python.exe" (
  echo [错误] 找不到 .venv\Scripts\python.exe
  pause
  exit /b 1
)
set D01_MODULE=my_d01_analysis
".venv\Scripts\python.exe" -m pytest "src\test_d01_analysis.py" -v
set D01_MODULE=
echo.
echo ------------------------------------------------------------
echo  退出码 = %ERRORLEVEL%   （0 = 全部通过）
echo ------------------------------------------------------------
pause

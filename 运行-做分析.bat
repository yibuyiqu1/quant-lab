@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo ============================================================
echo  运行：Day 1 分析（统计 + 三张图）
echo ============================================================
echo.
if not exist ".venv\Scripts\python.exe" (
  echo [错误] 找不到 .venv\Scripts\python.exe
  echo 请先在项目根目录运行：  python src\make_venv.py
  echo.
  pause
  exit /b 1
)
".venv\Scripts\python.exe" "src\my_d01_analysis.py"
echo.
echo ------------------------------------------------------------
echo  退出码 = %ERRORLEVEL%   （0 = 成功）
echo ------------------------------------------------------------
pause

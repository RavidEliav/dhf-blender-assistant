@echo off
setlocal
cd /d "%~dp0"

if not exist ".venv\Scripts\python.exe" (
    echo Creating virtual environment...
    python -m venv .venv || goto :error
)

echo Installing / checking dependencies...
".venv\Scripts\python.exe" -m pip install --quiet --disable-pip-version-check -r requirements.txt || goto :error

if not exist ".env" (
    copy ".env.example" ".env" >nul
    echo Created .env - add your GEMINI_API_KEY there, or enter it in the app sidebar.
)

".venv\Scripts\python.exe" -m streamlit run app.py --server.address localhost
goto :eof

:error
echo.
echo Setup failed. Make sure Python 3.10+ is installed and on PATH.
pause
exit /b 1

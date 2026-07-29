@echo off
setlocal
set "VENV_PY=%TEMP%\soporte_venv\Scripts\python.exe"
if not exist "%VENV_PY%" (
    echo Error: Virtual environment not found at %VENV_PY%
    echo Run: winget install Python.Python.3.12
    echo Then: C:\Users\emylu\AppData\Local\Programs\Python\Python312\python.exe -m venv "%TEMP%\soporte_venv"
    echo Then: "%TEMP%\soporte_venv\Scripts\pip" install -r requirements.txt
    pause
    exit /b 1
)
"%VENV_PY%" "%~dp0core\detectar.py"
pause

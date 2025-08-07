@echo off
chcp 65001 >nul
REM Скрипт для запуска Streamlit-приложения ИИ-Голос

REM --- Проверка наличия Python ---
python --version >nul 2>&1
if errorlevel 1 (
    echo Python не найден! Пожалуйста, установите Python 3.8+ и добавьте в PATH.
    pause
    exit /b
)

REM --- Проверка наличия pip ---
pip --version >nul 2>&1
if errorlevel 1 (
    echo pip не найден! Пожалуйста, установите pip и добавьте в PATH.
    pause
    exit /b
)

REM --- Проверка нужных модулей ---
set NEED_INSTALL=0

python -c "import streamlit" >nul 2>&1 || set NEED_INSTALL=1
python -c "import edge_tts" >nul 2>&1 || set NEED_INSTALL=1
python -c "import pydub" >nul 2>&1 || set NEED_INSTALL=1

if %NEED_INSTALL%==1 (
    echo Устанавливаются отсутствующие зависимости...
    pip install -r requirements.txt
) else (
    echo Зависимости уже установлены.
)

REM --- Запуск приложения ---
streamlit run app.py
pause

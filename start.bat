@echo off
REM Скрипт для запуска Streamlit-приложения ИИ-Голос

REM Проверка наличия Python
python --version >nul 2>&1
if errorlevel 1 (
    echo Python не найден! Пожалуйста, установите Python 3.8+ и добавьте в PATH.
    pause
    exit /b
)

REM Проверка наличия pip
pip --version >nul 2>&1
if errorlevel 1 (
    echo pip не найден! Пожалуйста, установите pip и добавьте в PATH.
    pause
    exit /b
)

REM Установка зависимостей
pip install -r requirements.txt

REM Запуск приложения
streamlit run app.py
pause
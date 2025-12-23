@echo off
chcp 65001 >nul
echo   GIS Sync System - Backend Launcher


REM Проверка виртуального окружения
if not exist "venv\" (
    echo [ERROR] Виртуальное окружение не найдено.
    echo.
    echo Запустите сначала установку:
    echo   python scripts\setup_database.py
    echo.
    pause
    exit /b 1
)

REM Проверка зависимостей
if not exist "venv\Scripts\uvicorn.exe" (
    echo [ERROR] uvicorn не найден в виртуальном окружении.
    echo.
    echo Установите зависимости:
    echo   venv\Scripts\pip install uvicorn[standard]
    echo.
    pause
    exit /b 1
)

echo [INFO] Запуск FastAPI сервера...
echo [INFO] Сервер будет доступен по: http://localhost:8000
echo [INFO] Документация: http://localhost:8000/docs
echo [INFO] Админка: http://localhost:8000/admin
echo.
echo [INFO] Для остановки сервера нажмите Ctrl+C
echo.

REM Запуск сервера
venv\Scripts\uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

if %errorlevel% neq 0 (
    echo.
    echo [ERROR] Не удалось запустить сервер.
    pause
)
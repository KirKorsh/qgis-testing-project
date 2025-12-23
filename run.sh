#!/bin/bash

echo "  GIS Sync System - Backend Launcher"

# Проверка виртуального окружения
if [ ! -d "venv" ]; then
    echo "[ERROR] Виртуальное окружение не найдено."
    echo ""
    echo "Запустите сначала установку:"
    echo "  python3 setup.py"
    echo ""
    exit 1
fi

# Проверка Python в venv
if [ ! -f "venv/bin/python" ]; then
    echo "[ERROR] Python в виртуальном окружении не найден."
    echo ""
    echo "Переустановите виртуальное окружение:"
    echo "  python3 setup.py"
    echo ""
    exit 1
fi

# Проверка зависимостей
echo "[INFO] Проверка зависимостей..."
venv/bin/python -c "import uvicorn" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "[ERROR] uvicorn не установлен."
    echo ""
    echo "Установите зависимости:"
    echo "  venv/bin/pip install uvicorn[standard]"
    echo ""
    exit 1
fi

# Проверка .env файла
if [ ! -f ".env" ]; then
    echo "[WARNING] Файл .env не найден."
    echo ""
    echo "Будет использоваться конфигурация по умолчанию."
    echo "Для настройки запустите: python3 setup.py"
    echo ""
fi

echo "[INFO] Запуск FastAPI сервера..."
echo "[INFO] Сервер будет доступен по: http://localhost:8000"
echo "[INFO] Документация: http://localhost:8000/docs"
echo "[INFO] Админка: http://localhost:8000/admin"
echo ""
echo "[INFO] Для остановки сервера нажмите Ctrl+C"
echo ""

# Запуск сервера через Python модуль
venv/bin/python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

if [ $? -ne 0 ]; then
    echo ""
    echo "[ERROR] Не удалось запустить сервер."
    echo ""
    echo "Возможные решения:"
    echo "1. Проверьте установку зависимостей: venv/bin/pip list"
    echo "2. Переустановите зависимости: venv/bin/pip install -r requirements.txt"
    echo "3. Запустите установку заново: python3 setup.py"
    echo ""
    exit 1
fi
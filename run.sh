
echo "GIS Sync System - Backend Launcher"

# Проверка виртуального окружения
if [ ! -d "venv" ]; then
    echo "[ERROR] Виртуальное окружение не найдено."
    echo ""
    echo "Запустите сначала установку:"
    echo "  python setup.py"
    echo ""
    exit 1
fi

# Проверка uvicorn
if [ ! -f "venv/bin/uvicorn" ]; then
    echo "[ERROR] uvicorn не найден в виртуальном окружении."
    echo ""
    echo "Установите зависимости:"
    echo "  venv/bin/pip install uvicorn[standard] fastapi"
    echo ""
    exit 1
fi

echo "[INFO] Запуск FastAPI сервера..."
echo "[INFO] Сервер будет доступен по: http://localhost:8000"
echo "[INFO] Документация: http://localhost:8000/docs"
echo "[INFO] Админка: http://localhost:8000/admin"
echo ""
echo "[INFO] Для остановки сервера нажмите Ctrl+C"
echo ""

# Активация venv и запуск
source venv/bin/activate
python -c "import sys; print(f'Python версия: {sys.version}')"
echo ""

# Запуск сервера
exec uvicorn app.main:app --reload --host 0.0.0.0 --port 

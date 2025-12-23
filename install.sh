
echo "  GIS Sync System - Установка"
 

echo "[INFO] Запуск автоматической установки..."
echo "[INFO] Для прерывания установки нажмите Ctrl+C"
echo ""

# Проверка наличия Python3
if ! command -v python3 &> /dev/null; then
    echo "[ERROR] Python3 не найден в системе."
    echo ""
    echo "Установите Python3 командой:"
    echo "  Ubuntu/Debian: sudo apt-get install python3 python3-pip"
    echo "  CentOS/RHEL: sudo yum install python3 python3-pip"
    echo "  macOS: brew install python3"
    echo ""
    exit 1
fi

# Проверка наличия virtualenv
if ! python3 -m venv --help &> /dev/null; then
    echo "[WARNING] Модуль venv не найден."
    echo "Установка модуля venv..."
    if command -v apt-get &> /dev/null; then
        sudo apt-get install python3-venv -y
    elif command -v yum &> /dev/null; then
        sudo yum install python3-venv -y
    else
        echo "Установите python3-venv вручную"
    fi
fi

# Запуск установщика
python3 setup.py

if [ $? -ne 0 ]; then
    echo ""
    echo "[ERROR] Установка завершилась с ошибкой."
    echo "Проверьте сообщения выше для диагностики."
    exit 1
fi

echo ""
echo "  Установка успешно завершена!"
echo ""
echo "Для запуска сервера выполните:"
echo "  chmod +x run.sh"
echo "  ./run.sh"
echo ""
echo "Или откройте файл run.sh для просмотра инструкций"
echo ""
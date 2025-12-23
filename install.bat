@echo off
chcp 1251 >nul
echo   GIS Sync System - Установка

echo [INFO] Запуск автоматической установки...
echo [INFO] Для прерывания установки закройте это окно
echo [INFO] Или нажмите Ctrl+C
echo.

REM Проверка наличия Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python не найден в системе.
    echo.
    echo Установите Python с официального сайта:
    echo https://www.python.org/downloads/
    echo.
    echo Не забудьте отметить галочку "Add Python to PATH"
    echo.
    pause
    exit /b 1
)

REM Проверка версии Python
python -c "import sys; exit(0) if sys.version_info >= (3, 8) else exit(1)" 2>nul
if errorlevel 1 (
    echo [ERROR] Требуется Python 3.8 или выше
    echo.
    echo Установите актуальную версию Python
    echo.
    pause
    exit /b 1
)

REM Запуск установщика
echo [INFO] Запуск установщика setup.py...
python setup.py

if errorlevel 1 (
    echo.
    echo [ERROR] Установка завершилась с ошибкой.
    echo Проверьте сообщения выше для диагностики.
    pause
    exit /b 1
)

echo.
echo   Установка успешно завершена!
echo.
echo Для запуска сервера дважды кликните на файл run.bat
echo Или откройте его в текстовом редакторе для просмотра
echo.
pause
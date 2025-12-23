# Руководство по установке и использованию GIS Sync System

## Быстрая установка (рекомендуется)

### Для Windows:
1. **Скачайте проект** на компьютер
2. **Дважды кликните** на файл `install.bat`
3. **Следуйте инструкциям** на экране
4. После установки **дважды кликните** на `run.bat` для запуска сервера

### Для Linux/macOS:
```bash
# 1. Скачайте проект и перейдите в его папку
# 2. Сделайте скрипты исполняемыми
chmod +x install.sh run.sh

# 3. Запустите установку
./install.sh

# 4. Запустите сервер
./run.sh
```

## 1. Установка и настройка базы данных PostgreSQL

### Предварительные требования
- Установленный PostgreSQL 12 или выше
- Клиентские утилиты PostgreSQL (`psql`) должны быть доступны в PATH
- Права пользователя на создание баз данных

**Примечание для Linux/macOS:**
```bash
# Установка клиента PostgreSQL на Debian/Ubuntu
sudo apt-get install postgresql-client

# Установка на macOS (используя Homebrew)
brew install postgresql
```

### Автоматическая установка через скрипты (рекомендуемый способ)

**Windows** (дважды кликнуть): `install.bat`
**Linux/macOS:** `./install.sh`

Установщик выполнит следующие действия:
- Проверка наличия Python и необходимых компонентов
- Запрос параметров подключения к PostgreSQL (хост, порт, пользователь, пароль)
- Создание базы данных с указанным именем (по умолчанию `gis_test`)
- Включение расширения PostGIS в созданной базе данных
- Создание виртуального окружения Python и установка всех зависимостей
- Применение миграций Alembic для создания схемы таблиц

### Ручная установка (если автоматическая не сработала)

Если установщик не смог создать базу данных автоматически, выполните следующие шаги вручную:

#### Через командную строку:
```bash
# Подключитесь к PostgreSQL как пользователь с правами создания БД
psql -U postgres -h localhost

# В интерактивной сессии psql выполните:
CREATE DATABASE gis_test;
\c gis_test
CREATE EXTENSION IF NOT EXISTS postgis;
\q
```

#### Через pgAdmin4:
1. Откройте pgAdmin4
2. Подключитесь к серверу PostgreSQL
3. Щелкните правой кнопкой мыши по "Databases" и выберите "Create" → "Database"
4. Укажите имя базы данных (например, `gis_test`)
5. Нажмите "Save"
6. Откройте созданную базу данных
7. Откройте Query Tool и выполните:
```sql
CREATE EXTENSION IF NOT EXISTS postgis;
```

### Проверка установки базы данных
После создания базы данных проверьте ее доступность:
```bash
psql -U postgres -d gis_test -c "SELECT PostGIS_Version();"
```
Ожидаемый результат: отображение версии установленного PostGIS.

## 2. Установка плагина QGIS

Плагин находится в архиве `qgis-plugin.zip` репозитория.

#### Способ 1: Установка из ZIP-архива (рекомендуется)
1. Откройте QGIS
2. Перейдите в меню: Расширения → Управление расширениями и установкой расширений
3. Нажмите кнопку "Установить из ZIP"
4. Выберите созданный архив `qgis_plugin.zip`
5. Нажмите "Установить плагин"
6. Перезапустите QGIS

#### Способ 2: Ручное копирование
Скопируйте папку `qgis-plugin` из архива в директорию плагинов QGIS:

**Windows:**
```
%APPDATA%\QGIS\QGIS3\profiles\default\python\plugins\
```
Или полный путь:
```
C:\Users\ВАШ_ПОЛЬЗОВАТЕЛЬ\AppData\Roaming\QGIS\QGIS3\profiles\default\python\plugins\
```

**Linux:**
```
~/.local/share/QGIS/QGIS3/profiles/default/python/plugins/
```

**macOS:**
```
~/Library/Application Support/QGIS/QGIS3/profiles/default/python/plugins/
```

После копирования:
1. Перезапустите QGIS
2. Перейдите в Расширения → Управление расширениями
3. Найдите в списке "FastAPI Sync"
4. Установите флажок для активации плагина

### Проверка установки плагина
После перезапуска QGIS:
1. На панели инструментов должна появиться новая кнопка "Синхронизировать"
2. В меню Плагины должен появиться пункт "FastAPI Sync"

## 3. Запуск сервера базы данных

### Проверка состояния PostgreSQL

**Windows:**
```powershell
# Проверка службы PostgreSQL
Get-Service postgresql*

# Запуск службы (если не запущена)
Start-Service postgresql-x64-15  # укажите вашу версию
```

**Linux (systemd):**
```bash
# Проверка службы PostgreSQL
sudo systemctl status postgresql

# Запуск службы (если не запущена)
sudo systemctl start postgresql
```

**Linux (service):**
```bash
# Альтернативный способ для старых систем
sudo service postgresql status
sudo service postgresql start
```

**macOS (Homebrew):**
```bash
# Проверка службы PostgreSQL
brew services list | grep postgresql

# Запуск службы (если не запущена)
brew services start postgresql
```


### Проверка работоспособности сервера
После запуска сервера откройте в браузере:
- http://localhost:8000 - стандартная страница для перехода в административный интерфейс (админку)
- http://localhost:8000/admin - административный интерфейс
- http://localhost:8000/features - список геообъектов (должен вернуть пустой массив или существующие объекты)
- http://localhost:8000/docs - интерактивная документация API (Swagger UI)

!!!ПОСЛЕ СОХРАНЕНИЯ ИЗМЕНЕНИЙ СЛОЯ В QGIS ДЛЯ ОТОБРАЖЕНИЯ ИЗМЕНЕНИЯ В АДМИНКЕ НЕОБХОДИМО ПЕРЕЗАГРУЗИТЬ СТРАНИЦУ!!!

## 4. Использование вспомогательных скриптов

### check_db.py
Скрипт для проверки состояния базы данных и создания таблиц при необходимости.

**Основные команды:**

**Windows:**
```bash
python check_db.py
```

**Linux/macOS:**
```bash
python3 check_db.py
```

**Дополнительные опции:**
```bash
# Проверить состояние с подробным выводом
python check_db.py --check  # Windows
python3 check_db.py --check  # Linux/macOS

# Создать таблицы вручную (если миграции не сработали)
python check_db.py --create-tables
python3 check_db.py --create-tables

# Проверить конкретные аспекты БД
python check_db.py --check-tables
python check_db.py --check-postgis
```

**Результаты выполнения:**
- Проверка подключения к PostgreSQL
- Проверка существования таблицы `features`
- Проверка включения расширения PostGIS
- Проверка таблицы `alembic_version`
- Количество записей в таблице `features`

### debug_connection.py
Скрипт для диагностики проблем с подключением и конфигурацией.

**Использование:**

**Windows:**
```bash
python debug_connection.py
```

**Linux/macOS:**
```bash
python3 debug_connection.py
```

**Что проверяет скрипт:**
1. Чтение и валидация переменных окружения из `.env`
2. Проверка формата и содержания строки подключения к БД
3. Обнаружение невидимых символов или проблем с кодировкой
4. Формирование полного URL для подключения к БД

**Пример вывода:**
```
ПРОВЕРКА ПЕРЕМЕННЫХ ОКРУЖЕНИЯ
POSTGRES_HOST: 'localhost'
POSTGRES_PORT: '5432'
POSTGRES_DB: 'gis_test'
POSTGRES_USER: 'postgres'
POSTGRES_PASSWORD: '***'

ПРОВЕРКА config.py
DATABASE_URL: postgresql+psycopg2://postgres:***@localhost:5432/gis_test
Длина URL: 57
```

### test_alembic_connection.py
Скрипт для тестирования подключения Alembic к базе данных и проверки миграций.

**Использование:**

**Windows:**
```bash
python test_alembic_connection.py
```

**Linux/macOS:**
```bash
python3 test_alembic_connection.py
```

**Что проверяет скрипт:**
1. Чтение конфигурации из `alembic.ini`
2. Проверка строки подключения в конфигурации Alembic
3. Тестирование подключения к базе данных
4. Проверка существования таблицы `alembic_version`
5. Поиск и отображение доступных файлов миграций

**Типичные проблемы и решения:**

1. **Ошибка: "sqlalchemy.url = driver://user:pass@localhost/dbname"**
   Решение: Обновите `alembic.ini` с правильной строкой подключения

2. **Ошибка: "Таблица alembic_version не существует"**
   Решение: Создайте таблицу вручную или примените миграции

3. **Ошибка подключения к БД**
   Решение: Проверьте параметры в `.env` и доступность PostgreSQL

### Интеграция скриптов в процесс отладки

**Полный процесс отладки при проблемах с подключением:**

1. Сначала проверьте базовое подключение:
   ```bash
   python debug_connection.py  # Windows
   python3 debug_connection.py  # Linux/macOS
   ```

2. Если переменные окружения в порядке, проверьте Alembic:
   ```bash
   python test_alembic_connection.py
   python3 test_alembic_connection.py
   ```

3. Если Alembic не видит таблиц, создайте их вручную:
   ```bash
   python check_db.py --create-tables
   python3 check_db.py --create-tables
   ```

4. Проверьте общее состояние системы:
   ```bash
   python check_db.py --check
   python3 check_db.py --check
   ```

## Устранение неполадок

### Если установка не запускается:

**Windows:**
1. Убедитесь, что Python установлен и добавлен в PATH
   - Откройте командную строку и введите `python --version`
   - Если команда не работает, переустановите Python с галочкой "Add Python to PATH"
2. Проверьте, не блокирует ли антивирус выполнение скриптов

**Linux/macOS:**
1. Убедитесь, что файлы имеют права на выполнение
   ```bash
   chmod +x install.sh run.sh
   ```
2. Если нет Python3:
   ```bash
   sudo apt-get install python3 python3-pip python3-venv
   ```

### Автоматическое восстановление при проблемах

Если система не запускается из-за проблем с БД, выполните полный сброс:

**Windows:**
```bash
# 1. Остановите сервер (Ctrl+C в окне run.bat)
# 2. Удалите виртуальное окружение и конфигурацию
rmdir /s venv
del .env

# 3. Пересоздайте базу данных
psql -U postgres -c "DROP DATABASE IF EXISTS gis_test;"
psql -U postgres -c "CREATE DATABASE gis_test;"
psql -U postgres -d gis_test -c "CREATE EXTENSION IF NOT EXISTS postgis;"

# 4. Запустите установку заново (дважды кликните install.bat)
```

**Linux/macOS:**
```bash
# 1. Остановите сервер (Ctrl+C в терминале)
# 2. Удалите виртуальное окружение и конфигурацию
rm -rf venv .env

# 3. Пересоздайте базу данных
psql -U postgres -c "DROP DATABASE IF EXISTS gis_test;"
psql -U postgres -c "CREATE DATABASE gis_test;"
psql -U postgres -d gis_test -c "CREATE EXTENSION IF NOT EXISTS postgis;"

# 4. Запустите установку заново
chmod +x install.sh
./install.sh
```

### Логирование ошибок

Все вспомогательные скрипты выводят подробные сообщения об ошибках. Для более детального анализа можно включить логирование SQLAlchemy, добавив в `.env`:
```
SQLALCHEMY_ECHO=True
```

Это позволит видеть все SQL-запросы, которые выполняются при подключении к базе данных.


**Примечание:** Все скрипты предполагают, что вы находитесь в корневой директории проекта. Для автоматической установки скрипты вызываются из `setup.py` и не требуют ручного запуска.

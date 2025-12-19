
import os
import sys
import subprocess
import platform
import time

def run_command(cmd, env=None, capture_output=True):
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=capture_output,
            text=True,
            env=env or os.environ,
            timeout=30
        )
        if result.returncode != 0 and capture_output:
            print(f"Ошибка: {result.stderr[:200]}")
        return result.returncode == 0
    except subprocess.TimeoutExpired:
        print(f"Таймаут выполнения: {cmd}")
        return False

def check_postgresql_connection(host, port, user, password):
    print("Проверка подключения к PostgreSQL...")
    
    # Разные способы подключения
    test_commands = [
        # Через psql
        f'psql "postgresql://{user}:{password}@{host}:{port}/postgres" -c "SELECT 1"',
        # Через PGPASSWORD
        f'PGPASSWORD={password} psql -h {host} -p {port} -U {user} -d postgres -c "SELECT 1"',
    ]
    
    for cmd in test_commands:
        if run_command(cmd, capture_output=False):
            print(f"Подключение к PostgreSQL успешно")
            return True
    
    print(f"Не удалось подключиться к PostgreSQL")
    print(f"Убедитесь, что PostgreSQL запущен на {host}:{port}")
    print(f"Пользователь: {user}, пароль: {'*' * len(password)}")
    return False

def create_database(host, port, user, password, db_name):
    print(f"Создание базы данных {db_name}...")
    
    # Проверка существования БД
    check_db_cmd = f'psql "postgresql://{user}:{password}@{host}:{port}/postgres" -c "SELECT 1 FROM pg_database WHERE datname = \'{db_name}\'" -t'
    
    if run_command(check_db_cmd, capture_output=True):
        print(f"База данных {db_name} уже существует")
        return True
    
    # Создание БД
    create_cmd = f'psql "postgresql://{user}:{password}@{host}:{port}/postgres" -c "CREATE DATABASE {db_name}"'
    
    if run_command(create_cmd):
        print(f"База данных {db_name} создана")
        
        # Включение PostGIS
        enable_postgis = f'psql "postgresql://{user}:{password}@{host}:{port}/{db_name}" -c "CREATE EXTENSION IF NOT EXISTS postgis"'
        if run_command(enable_postgis):
            print("Расширение PostGIS включено")
            return True
    
    print(f"Не удалось создать базу данных {db_name}")
    return False

def setup_virtualenv():
    print("Создание виртуального окружения...")
    
    if os.path.exists("venv"):
        response = input("Виртуальное окружение уже существует. Пересоздать? (y/N): ")
        if response.lower() == 'y':
            import shutil
            shutil.rmtree("venv")
        else:
            print("Используется существующее окружение")
            return True
    
    return run_command(f"{sys.executable} -m venv venv")

def install_dependencies():
    print("Установка зависимостей...")
    
    pip_cmd = "venv\\Scripts\\pip" if platform.system() == "Windows" else "venv/bin/pip"
    
    if os.path.exists("requirements.txt"):
        return run_command(f"{pip_cmd} install -r requirements.txt")
    
    # Базовые зависимости
    deps = [
        "fastapi>=0.104.1",
        "uvicorn[standard]>=0.24.0",
        "sqlalchemy>=2.0.23",
        "geoalchemy2>=0.14.2",
        "psycopg2-binary>=2.9.9",
        "alembic>=1.12.1",
        "python-dotenv>=1.0.0",
        "shapely>=2.0.2"
    ]
    
    if run_command(f"{pip_cmd} install {' '.join(deps)}"):
        run_command(f"{pip_cmd} freeze > requirements.txt")
        return True
    
    return False

def setup_environment(db_config):
    print("Настройка конфигурации...")
    
    env_content = f"""# PostgreSQL Configuration
POSTGRES_HOST={db_config['host']}
POSTGRES_PORT={db_config['port']}
POSTGRES_DB={db_config['db_name']}
POSTGRES_USER={db_config['user']}
POSTGRES_PASSWORD={db_config['password']}
"""
    
    try:
        with open(".env", "w", encoding="utf-8") as f:
            f.write(env_content)
        
        # Пример без пароля
        example = f"""POSTGRES_HOST={db_config['host']}
POSTGRES_PORT={db_config['port']}
POSTGRES_DB={db_config['db_name']}
POSTGRES_USER={db_config['user']}
POSTGRES_PASSWORD=1111
"""
        with open(".env.example", "w", encoding="utf-8") as f:
            f.write(example)
        
        return True
    except Exception as e:
        print(f"Ошибка создания .env: {e}")
        return False

def apply_migrations():
    print("Применение миграций базы данных...")
    
    python_cmd = "venv\\Scripts\\python" if platform.system() == "Windows" else "venv/bin/python"
    
    # Обновление alembic.ini с текущими настройками
    if os.path.exists(".env"):
        with open(".env", "r") as f:
            lines = f.readlines()
            config = {}
            for line in lines:
                if '=' in line:
                    key, value = line.strip().split('=', 1)
                    config[key] = value
            
            if all(k in config for k in ['POSTGRES_HOST', 'POSTGRES_PORT', 'POSTGRES_DB', 'POSTGRES_USER', 'POSTGRES_PASSWORD']):
                db_url = f"postgresql://{config['POSTGRES_USER']}:{config['POSTGRES_PASSWORD']}@{config['POSTGRES_HOST']}:{config['POSTGRES_PORT']}/{config['POSTGRES_DB']}"
                
                # Обновление alembic.ini
                if os.path.exists("alembic.ini"):
                    with open("alembic.ini", "r") as f_ini:
                        content = f_ini.read()
                    
                    # Обновление sqlalchemy.url
                    import re
                    new_content = re.sub(
                        r'sqlalchemy\.url\s*=.*',
                        f'sqlalchemy.url = {db_url}',
                        content
                    )
                    
                    with open("alembic.ini", "w") as f_ini:
                        f_ini.write(new_content)
    
    return run_command(f"{python_cmd} -m alembic upgrade head")

def get_database_config():
    print("\n" + "="*50)
    print("Настройка подключения к PostgreSQL")
    print("="*50)
    
    config = {
        'host': 'localhost',
        'port': '5432',
        'db_name': 'gis_test',
        'user': 'postgres',
        'password': ''
    }
    
    config['host'] = input(f"Хост PostgreSQL [{config['host']}]: ").strip() or config['host']
    config['port'] = input(f"Порт [{config['port']}]: ").strip() or config['port']
    config['db_name'] = input(f"Имя базы данных [{config['db_name']}]: ").strip() or config['db_name']
    config['user'] = input(f"Пользователь [{config['user']}]: ").strip() or config['user']
    config['password'] = input(f"Пароль для {config['user']}: ").strip()
    
    return config

def main():
    print("="*50)
    print("Установка GIS Sync System")
    print("="*50)
    
    # Получение конфигурации БД
    db_config = get_database_config()
    
    # Проверка подключения к PostgreSQL
    if not check_postgresql_connection(
        db_config['host'],
        db_config['port'],
        db_config['user'],
        db_config['password']
    ):
        print("\nНе удалось подключиться к PostgreSQL.")
        print("Убедитесь, что PostgreSQL запущен и доступен.")
        return False
    
    # Создание базы данных
    if not create_database(
        db_config['host'],
        db_config['port'],
        db_config['user'],
        db_config['password'],
        db_config['db_name']
    ):
        print("\nНе удалось создать базу данных.")
        return False
    
    # Создание виртуального окружения
    if not setup_virtualenv():
        print("\nНе удалось создать виртуальное окружение.")
        return False
    
    # Устанавливка зависимости
    if not install_dependencies():
        print("\nНе удалось установить зависимости.")
        return False
    
    # Настройка окружения
    if not setup_environment(db_config):
        print("\nНе удалось настроить конфигурацию.")
        return False
    
    # Применение миграции
    if not apply_migrations():
        print("\nНе удалось применить миграции.")
        return False
    
    print("Установка завершена успешно!")
    
    if platform.system() == "Windows":
        print("\nДля запуска сервера выполните: run.bat")
    else:
        print("\nДля запуска сервера выполните: ./run.sh")
    
    print("\nДалее следуйте инструкции в README.md")
    return True

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\nУстановка прервана пользователем.")
        sys.exit(1)
    except Exception as e:
        print(f"\nНеожиданная ошибка: {e}")
        sys.exit(1)
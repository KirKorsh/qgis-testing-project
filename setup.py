import os
import sys
import subprocess
import platform
import time
from urllib.parse import quote

def run_command(cmd, env=None, capture_output=True):
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=capture_output,
            text=True,
            encoding='utf-8',
            env=env or os.environ,
            timeout=30
        )
        
        if result.returncode != 0 and capture_output:
            print(f"  Ошибка: {result.stderr[:200]}")
        return result.returncode == 0
        
    except subprocess.TimeoutExpired:
        print(f"  Таймаут выполнения: {cmd}")
        return False
    except FileNotFoundError:
        print(f"  Команда не найдена: {cmd.split()[0]}")
        return False

def check_postgresql_connection(host, port, user, password):
    """Проверка подключения через SQLAlchemy"""
    print("Проверка подключения к PostgreSQL...")
    
    try:
        # Формируем URL подключения
        db_url = f"postgresql://{user}:{password}@{host}:{port}/postgres"
        
        # Создаем движок SQLAlchemy
        from sqlalchemy import create_engine, text
        
        engine = create_engine(db_url, echo=False, pool_pre_ping=True)
        
        # Пробуем подключиться
        with engine.connect() as connection:
            # Выполняем простой запрос
            result = connection.execute(text("SELECT 1"))
            test_result = result.scalar()
            
            if test_result == 1:
                print("  Подключение к PostgreSQL успешно")
                return True
            else:
                print("  Неожиданный результат проверки")
                return False
                
    except Exception as e:
        error_msg = str(e)
        print(f"  Не удалось подключиться к PostgreSQL")
        print(f"  Ошибка: {error_msg[:100]}")
        print(f"  Убедитесь, что PostgreSQL запущен на {host}:{port}")
        print(f"  Пользователь: {user}, пароль: {'*' * len(password)}")
        
        # Подсказки для частых ошибок
        if "password authentication failed" in error_msg:
            print(f"  Подсказка: Неверный пароль для пользователя {user}")
        elif "could not connect to server" in error_msg:
            print(f"  Подсказка: PostgreSQL не запущен или недоступен")
        elif "database" in error_msg and "does not exist" in error_msg:
            print(f"  Подсказка: База данных 'postgres' не существует")
        
        return False

def create_database(host, port, user, password, db_name):
    print(f"Создание базы данных {db_name}...")
    
    try:
        from sqlalchemy import create_engine, text
        
        # Подключаемся к стандартной БД postgres для создания новой
        admin_db_url = f"postgresql://{user}:{password}@{host}:{port}/postgres"
        admin_engine = create_engine(admin_db_url)
        
        # Проверяем существование БД
        with admin_engine.connect() as conn:
            result = conn.execute(
                text("SELECT 1 FROM pg_database WHERE datname = :db_name"),
                {"db_name": db_name}
            )
            
            if result.fetchone():
                print(f"  База данных {db_name} уже существует")
                return True
        
        # Создание новой БД
        with admin_engine.connect() as conn:
            # Закрываем транзакцию перед созданием БД
            conn.execute(text("COMMIT"))
            conn.execute(text(f"CREATE DATABASE {db_name}"))
        
        print(f"  База данных {db_name} создана")
        
        # Подключение к новой БД для создания PostGIS
        new_db_url = f"postgresql://{user}:{password}@{host}:{port}/{db_name}"
        new_engine = create_engine(new_db_url)
        
        with new_engine.connect() as conn:
            conn.execute(text("CREATE EXTENSION IF NOT EXISTS postgis"))
        
        print("  Расширение PostGIS включено")
        return True
        
    except Exception as e:
        print(f"  Не удалось создать базу данных {db_name}: {e}")
        return False
def setup_virtualenv():
    print("Создание виртуального окружения...")
    
    if os.path.exists("venv"):
        response = input("  Виртуальное окружение уже существует. Пересоздать? (y/N): ")
        if response.lower() == 'y':
            import shutil
            shutil.rmtree("venv")
        else:
            print("  Использование существующего окружения")
            return True
    
    return run_command(f"{sys.executable} -m venv venv")

def install_dependencies():
    print("Установка зависимостей...")
    
    if platform.system() == "Windows":
        pip_cmd = "venv\\Scripts\\pip"
    else:
        pip_cmd = "venv/bin/pip"
    
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
        print(f"  Ошибка создания .env: {e}")
        return False

def apply_migrations():
    print("Применение миграций базы данных...")
    
    if platform.system() == "Windows":
        venv_python_path = "venv\\Scripts\\python"
    else:  # Linux, macOS
        venv_python_path = "venv/bin/python"
    
    
    if os.path.exists(venv_python_path):
        python_cmd = venv_python_path
    else:
        print("  Внимание: venv не найден, использование системного Python")
        python_cmd = "python"
    
    # Обновление alembic.ini с текущими настройками
    if os.path.exists(".env"):
        with open(".env", "r", encoding="utf-8") as f:
            lines = f.readlines()
            config = {}
            for line in lines:
                line = line.strip()
                if line and '=' in line and not line.startswith('#'):
                    key, value = line.split('=', 1)
                    config[key.strip()] = value.strip()
            
            required_keys = ['POSTGRES_HOST', 'POSTGRES_PORT', 'POSTGRES_DB', 'POSTGRES_USER', 'POSTGRES_PASSWORD']
            if all(k in config for k in required_keys):
                # Экранирование пароля для URL
                safe_password = quote(config['POSTGRES_PASSWORD'], safe='')
                db_url = f"postgresql://{config['POSTGRES_USER']}:{safe_password}@{config['POSTGRES_HOST']}:{config['POSTGRES_PORT']}/{config['POSTGRES_DB']}"
                
                if os.path.exists("alembic.ini"):
                    with open("alembic.ini", "r", encoding="utf-8") as f_ini:
                        content = f_ini.read()
                    
                    import re
                    new_content = re.sub(
                        r'sqlalchemy\.url\s*=.*',
                        f'sqlalchemy.url = {db_url}',
                        content,
                        flags=re.DOTALL
                    )
                    
                    with open("alembic.ini", "w", encoding="utf-8") as f_ini:
                        f_ini.write(new_content)
    
    cmd = f"{python_cmd} -m alembic upgrade head"
    print(f"  Выполнение: {cmd}")
    
    return run_command(cmd)

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

def install_minimal_dependencies():
    print("Установка SQLAlchemy для проверки подключения...")
    
    # Определяем путь к pip
    if platform.system() == "Windows":
        pip_cmd = "venv\\Scripts\\pip"
    else:
        pip_cmd = "venv/bin/pip"
    
    # Минимальные зависимости для проверки подключения
    minimal_deps = [
        "sqlalchemy>=2.0.23",
        "psycopg2-binary>=2.9.9"  
    ]
    
    cmd = f"{pip_cmd} install {' '.join(minimal_deps)}"
    print(f"  Выполняю: {cmd}")
    
    return run_command(cmd)

def install_all_dependencies():
    print("Установка всех зависимостей...")
    
    if platform.system() == "Windows":
        pip_cmd = "venv\\Scripts\\pip"
    else:
        pip_cmd = "venv/bin/pip"
    
    if os.path.exists("requirements.txt"):
        return run_command(f"{pip_cmd} install -r requirements.txt")
    
    # Полный список зависимостей
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
    
    cmd = f"{pip_cmd} install {' '.join(deps)}"
    print(f"  Выполняю: {cmd}")
    
    if run_command(cmd):
        # Сохраняем зависимости
        run_command(f"{pip_cmd} freeze > requirements.txt")
        return True
    
    return False

def main():
    print("Установка GIS Sync System")
    
    # Создаем виртуальное окружение
    if not setup_virtualenv():
        print("\nНе удалось создать виртуальное окружение.")
        return False
    
    # Устанавливаем зависимости для проверки БД
    print("\nУстановка минимальных зависимостей для проверки подключения...")
    if not install_minimal_dependencies():
        print("\nНе удалось установить минимальные зависимости.")
        return False
    
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
    
    # Создаем базу данных
    if not create_database(
        db_config['host'],
        db_config['port'],
        db_config['user'],
        db_config['password'],
        db_config['db_name']
    ):
        print("\nНе удалось создать базу данных.")
        return False
    
    # Устанавливаем  зависимости
    print("\nУстановка всех зависимостей...")
    if not install_all_dependencies():
        print("\nНе удалось установить зависимости.")
        return False
    
    #  Настройка окружения
    if not setup_environment(db_config):
        print("\nНе удалось настроить конфигурацию.")
        return False
    
    #  Применение миграций
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
import os
import sys
import subprocess
import platform
import time
from urllib.parse import quote

def run_command(cmd, env=None, capture_output=True, timeout=60):
    # Исполнение команды через shell с обработкой кодировки Windows
    try:
        print(f"  [CMD] {cmd}")
        
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=capture_output,
            text=True,
            encoding='cp1251',
            errors='replace',
            env=env or os.environ,
            timeout=timeout
        )
        
        if capture_output:
            # Вывод stdout если есть
            if result.stdout and result.stdout.strip():
                for line in result.stdout.strip().split('\n'):
                    if line.strip():
                        print(f"    [OUT] {line}")
            
            # Вывод stderr если есть ошибка
            if result.returncode != 0 and result.stderr:
                for line in result.stderr.strip().split('\n'):
                    if line.strip():
                        print(f"    [ERR] {line}")
        
        return result.returncode == 0
        
    except subprocess.TimeoutExpired:
        print(f"  Таймаут выполнения ({timeout}с): {cmd}")
        return False
    except FileNotFoundError:
        print(f"  Команда не найдена: {cmd.split()[0] if ' ' in cmd else cmd}")
        return False
    except Exception as e:
        print(f"  Неожиданная ошибка: {type(e).__name__}: {e}")
        return False
        
def create_database(host, port, user, password, db_name):
    print(f"Создание базы данных {db_name}...")
    
    try:
        from sqlalchemy import create_engine, text
        
        # Подключение к стандартной БД postgres для создания новой
        admin_db_url = f"postgresql://{user}:{password}@{host}:{port}/postgres"
        admin_engine = create_engine(admin_db_url)
        
        # Проверка существование БД
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
    
    # Проверка существования venv
    if os.path.exists("venv"):
        response = input("  Виртуальное окружение уже существует. Пересоздать? (y/N): ")
        if response.lower() == 'y':
            import shutil
            try:
                shutil.rmtree("venv")
                print("  Старое окружение удалено")
            except Exception as e:
                print(f"  Ошибка удаления venv: {e}")
                return False
        else:
            print("  Использование существующего окружения")
            
            # Проверка, что в venv есть python
            if platform.system() == "Windows":
                python_path = "venv\\Scripts\\python.exe"
            else:
                python_path = "venv/bin/python"
            
            if os.path.exists(python_path):
                print(f"  Python найден в venv: {python_path}")
                return True
            else:
                print(f"  Ошибка: {python_path} не найден в venv")
                return False
    
    # Создание нового venv
    print("  Создание нового виртуального окружения...")
    
    # sys.executable для создания venv
    cmd = f'"{sys.executable}" -m venv venv'
    print(f"  Выполнение: {cmd}")
    
    if run_command(cmd, timeout=60):
        # Проверка успешности создания
        time.sleep(2)  # Даем время для создания файлов
        
        if platform.system() == "Windows":
            python_path = "venv\\Scripts\\python.exe"
            pip_path = "venv\\Scripts\\pip.exe"
        else:
            python_path = "venv/bin/python"
            pip_path = "venv/bin/pip"
        
        if os.path.exists(python_path):
            print(f"  Виртуальное окружение создано успешно")
            print(f"  Python путь: {python_path}")
            
            # Проверка версии Python
            version_cmd = f'"{python_path}" --version'
            run_command(version_cmd, timeout=10)
            
            return True
        else:
            print(f"  Ошибка: {python_path} не найден после создания venv")
            print("  Возможные причины:")
            print("    1. Модуль venv не установлен в системе")
            print("    2. Недостаточно прав для создания файлов")
            print("    3. Антивирус блокирует создание файлов")
            return False
    else:
        print("  Не удалось создать виртуальное окружение")
        
        # Альтернативные способы создания venv
        print("  Попробуйте создать venv вручную:")
        print(f"    {sys.executable} -m venv venv")
        print("  Или установите модуль venv:")
        print("    pip install virtualenv")
        
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

    venv_python = "venv\\Scripts\\python.exe" if platform.system() == "Windows" else "venv/bin/python"

    if not os.path.exists(venv_python):
        print("Python venv не найден")
        return False

    env = os.environ.copy()
    env["PYTHONPATH"] = os.getcwd()

    if not run_command(
        f'"{venv_python}" -m alembic upgrade head',
        env=env,
        timeout=120
    ):
        print("Ошибка применения миграций")
        return False

    print("Миграции успешно применены")
    return True


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
    print("  Установка SQLAlchemy и psycopg2...")
    
    if platform.system() == "Windows":
        pip_cmd = "venv\\Scripts\\pip"
    else:
        pip_cmd = "venv/bin/pip"
    
    minimal_deps = [
        "sqlalchemy>=2.0.23",
        "psycopg2-binary>=2.9.9"
    ]
    
    cmd = f'"{pip_cmd}" install {" ".join(minimal_deps)}'
    print(f"  Выполнение: {cmd}")
    
    return run_command(cmd)

def install_all_dependencies():
    print("  Установка FastAPI, GeoAlchemy2 и других зависимостей...")
    
    if platform.system() == "Windows":
        pip_cmd = "venv\\Scripts\\pip"
    else:
        pip_cmd = "venv/bin/pip"
    
    # Убираем --progress-bar, оставляем только --disable-pip-version-check
    pip_args = "--disable-pip-version-check"
    
    if os.path.exists("requirements.txt"):
        cmd = f'"{pip_cmd}" {pip_args} install -r requirements.txt'
        print(f"  Выполнение: {cmd}")
        return run_command(cmd, timeout=300)
    
    deps = [
        "fastapi>=0.104.1",
        "uvicorn[standard]>=0.24.0",
        "geoalchemy2>=0.14.2",
        "alembic>=1.12.1", 
        "python-dotenv>=1.0.0",
        "shapely>=2.0.2"
    ]
    
    cmd = f'"{pip_cmd}" {pip_args} install {" ".join(deps)}'
    print(f"  Выполнение: {cmd}")
    
    if run_command(cmd, timeout=300):
        # Сохранение зависимостей в requirements.txt
        run_command(f'"{pip_cmd}" freeze > requirements.txt', timeout=30)
        return True
    
    return False

def run_in_venv(python_code):
    if platform.system() == "Windows":
        python_path = "venv\\Scripts\\python"
    else:
        python_path = "venv/bin/python"
    
    # Создание временного файла 
    import tempfile
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False, encoding='utf-8') as f:
        f.write('# -*- coding: utf-8 -*-\n')
        f.write(python_code)
        temp_file = f.name
    
    try:
        # Выполнение кода через venv с захватом вывода
        cmd = f'"{python_path}" "{temp_file}"'
        result = run_command(cmd, capture_output=True)
        
        # Вывод результата выполнения
        if hasattr(result, 'stdout') and result.stdout:
            for line in result.stdout.strip().split('\n'):
                if line:
                    print(f"    {line}")
        
        return result
    finally:
        # Удаление временного файла
        import os
        os.unlink(temp_file)

def check_postgresql_connection_in_venv(host, port, user, password):

    print("Проверка подключения к PostgreSQL...")
    
    from urllib.parse import quote
    safe_password = quote(password, safe='')
    
    python_code = f'''
# -*- coding: utf-8 -*-
import sys
import traceback
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError

try:
    # Формирование URL подключения
    db_url = "postgresql://{user}:{safe_password}@{host}:{port}/postgres"
    print(f"Попытка подключения к: {{db_url}}")
    
    engine = create_engine(db_url, echo=False, connect_args={{"connect_timeout": 10}})
    
    # Проверка подключения
    with engine.connect() as connection:
        result = connection.execute(text("SELECT 1"))
        test_value = result.scalar()
        
        if test_value == 1:
            print("SUCCESS: Подключение успешно")
            sys.exit(0)
        else:
            print(f"ERROR: Неожиданный результат: {{test_value}}")
            sys.exit(1)
            
except Exception as e:
    print(f"ERROR_DETAILS: {{type(e).__name__}}: {{e}}")
    print("TRACEBACK:")
    traceback.print_exc()
    sys.exit(1)
'''
    
    print("  Запуск проверки подключения...")
    success = run_in_venv(python_code)
    
    if success:
        print("  Подключение к PostgreSQL успешно")
        return True
    else:
        print("  Не удалось подключиться к PostgreSQL")
        print(f"  Убедитесь, что PostgreSQL запущен на {host}:{port}")
        print(f"  Пользователь: {user}, пароль: {'*' * len(password)}")
        
        # Дополнительные проверки
        print("\n  Возможные решения:")
        print("  1. Проверьте, запущена ли служба PostgreSQL:")
        print("     - Win+R → services.msc → найдите 'PostgreSQL'")
        print("     - Или в PowerShell: Get-Service postgresql*")
        print("  2. Проверьте пароль пользователя postgres")
        print("  3. Проверьте, разрешены ли подключения в pg_hba.conf")
        print("  4. Попробуйте подключиться через pgAdmin4 или psql")
        
        return False
    
def create_database_in_venv(host, port, user, password, db_name):
    print(f"Создание базы данных {db_name}...")
    
    from urllib.parse import quote
    safe_password = quote(password, safe='')
    
    python_code = f'''
import sys
from sqlalchemy import create_engine, text

try:
    # Подключение к стандартной БД postgres
    admin_db_url = "postgresql://{user}:{safe_password}@{host}:{port}/postgres"
    admin_engine = create_engine(admin_db_url)
    
    # Проверка существования БД
    with admin_engine.connect() as conn:
        result = conn.execute(
            text("SELECT 1 FROM pg_database WHERE datname = :db_name"),
            {{"db_name": "{db_name}"}}
        )
        
        if result.fetchone():
            print("DATABASE_EXISTS")
            sys.exit(0)
    
    # Создание новой БД
    with admin_engine.connect() as conn:
        conn.execute(text("COMMIT"))
        conn.execute(text("CREATE DATABASE {db_name}"))
    
    print("DATABASE_CREATED")
    
    # Подключение к новой БД для создания PostGIS
    new_db_url = "postgresql://{user}:{safe_password}@{host}:{port}/{db_name}"
    new_engine = create_engine(new_db_url)
    
    with new_engine.connect() as conn:
        conn.execute(text("CREATE EXTENSION IF NOT EXISTS postgis"))
    
    print("POSTGIS_ENABLED")
    sys.exit(0)
    
except Exception as e:
    print(f"ERROR: {{e}}")
    sys.exit(1)
'''
    
    if run_in_venv(python_code):
        print(f"  База данных {db_name} создана")
        print("  Расширение PostGIS включено")
        return True
    else:
        print(f"  Не удалось создать базу данных {db_name}")
        return False

def main():
    print("Установка GIS Sync System")
    
    # Получение конфигурации БД
    db_config = get_database_config()
    
    if not setup_virtualenv():
        print("\nНе удалось создать виртуальное окружение.")
        return False
    
    print("\nУстановка SQLAlchemy для проверки подключения...")
    if not install_minimal_dependencies():
        print("\nНе удалось установить SQLAlchemy.")
        return False
    
    if not check_postgresql_connection_in_venv(
        db_config['host'],
        db_config['port'],
        db_config['user'],
        db_config['password']
    ):
        print("\nНе удалось подключиться к PostgreSQL.")
        print("Убедитесь, что PostgreSQL запущен и доступен.")
        return False
    
    # Создание базы данных через отдельный процесс в venv
    if not create_database_in_venv(
        db_config['host'],
        db_config['port'],
        db_config['user'],
        db_config['password'],
        db_config['db_name']
    ):
        print("\nНе удалось создать базу данных.")
        return False
    
    # Установка всех зависимостей
    print("\nУстановка всех зависимостей...")
    if not install_all_dependencies():
        print("\nНе удалось установить зависимости.")
        return False
    
    # Настройка окружения
    if not setup_environment(db_config):
        print("\nНе удалось настроить конфигурацию.")
        return False
    
    # Применение миграций
    if not apply_migrations():
        print("\nНе удалось применить миграции.")
        return False
    
    print("\n" + "="*50)
    print("Установка завершена успешно!")
    print("="*50)
    
    if platform.system() == "Windows":
        print("\nДля запуска сервера дважды кликните на run.bat")
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
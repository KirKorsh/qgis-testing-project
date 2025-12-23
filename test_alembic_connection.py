
import os
import sys
from alembic.config import Config
from sqlalchemy import create_engine, text

print(" ТЕСТ ПОДКЛЮЧЕНИЯ ALEMBIC ")

config = Config("alembic.ini")
db_url = config.get_main_option("sqlalchemy.url")
print(f"1. URL из alembic.ini: {db_url}")

print(f"\n2. Тестируем подключение к БД...")
try:
    engine = create_engine(db_url)
    with engine.connect() as conn:
        result = conn.execute(text("SELECT 1"))
        print(f"    Подключение успешно")
        
        # Проверка таблицы alembic_version
        try:
            result = conn.execute(text("SELECT version_num FROM alembic_version"))
            version = result.scalar()
            print(f"   Таблица alembic_version существует. Версия: {version}")
        except:
            print(f"    Таблица alembic_version не существует или пуста")
            
except Exception as e:
    print(f"    Ошибка подключения: {type(e).__name__}: {e}")
    print(f"   Подсказка: Проверьте, запущен ли PostgreSQL на localhost:5432")
    print(f"   Проверьте пароль в URL: {db_url[:50]}...")

# Проверка файлов миграции
print(f"\n3. Проверяем файлы миграций...")
import glob
migrations = glob.glob("alembic/versions/*.py")
print(f"   Найдено файлов миграций: {len(migrations)}")
for m in migrations:
    print(f"   - {os.path.basename(m)}")
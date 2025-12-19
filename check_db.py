
from app.database import engine
from sqlalchemy import text

print("Проверка подключения к базе данных...")

try:
    with engine.connect() as conn:
        # Проверка наличия таблицы features
        result = conn.execute(text("SELECT table_name FROM information_schema.tables WHERE table_name='features'"))
        
        if result.rowcount > 0:
            print('Таблица features создана успешно!')
            
            # Проверка структуры таблицы
            result = conn.execute(text("""
                SELECT column_name, data_type 
                FROM information_schema.columns 
                WHERE table_name='features' 
                ORDER BY ordinal_position
            """))
            
            print('\nСтруктура таблицы features:')
            for row in result:
                print(f'  {row[0]}: {row[1]}')
        else:
            print('Таблица features не найдена')
            
except Exception as e:
    print(f'Ошибка подключения: {e}')
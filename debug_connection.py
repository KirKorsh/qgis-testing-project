
import os
from dotenv import load_dotenv

load_dotenv()

print("ПРОВЕРКА ПЕРЕМЕННЫХ ОКРУЖЕНИЯ")
print(f"POSTGRES_HOST: '{os.getenv('POSTGRES_HOST')}'")
print(f"POSTGRES_PORT: '{os.getenv('POSTGRES_PORT')}'")
print(f"POSTGRES_DB: '{os.getenv('POSTGRES_DB')}'")
print(f"POSTGRES_USER: '{os.getenv('POSTGRES_USER')}'")
print(f"POSTGRES_PASSWORD: '{os.getenv('POSTGRES_PASSWORD')}'")

# Проверка на невидимые символы
for var in ['POSTGRES_HOST', 'POSTGRES_USER', 'POSTGRES_PASSWORD', 'POSTGRES_DB']:
    value = os.getenv(var)
    if value:
        print(f"\n{var} (коды символов):")
        for char in value:
            print(f"  '{char}' -> {ord(char)}")

print("\n ПРОВЕРКА config.py ")
from app.core.config import DATABASE_URL
print(f"DATABASE_URL: {DATABASE_URL}")
print(f"Длина URL: {len(DATABASE_URL)}")

# Проверка кодов символов в URL
print("\nКоды первых 70 символов URL:")
for i, char in enumerate(DATABASE_URL[:70]):
    print(f"  [{i}] '{char}' -> {ord(char)}")
from fastapi import FastAPI
from app.database import engine, Base
from app.models.feature import Feature
from app.api import feature as feature_router

app = FastAPI()

# Создаём таблицы
Base.metadata.create_all(bind=engine)

# Подключаем роутер
app.include_router(feature_router.router)

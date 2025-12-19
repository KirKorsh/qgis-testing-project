from fastapi import FastAPI, Request, Depends
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.crud import feature as crud
from app.api import feature as feature_router
from app.dependencies import get_db

app = FastAPI()

# Подключание роутеров API
app.include_router(feature_router.router)

# Подключение шаблоны и статические файлы
templates = Jinja2Templates(directory="app/templates")
app.mount("/static", StaticFiles(directory="app/static"), name="static")


@app.get("/")
def root(request: Request):
    return templates.TemplateResponse(
        "index.html",
        {"request": request}
    )

@app.get("/admin")
def admin_dashboard(request: Request, db: Session = Depends(get_db)): 
    stats = crud.get_stats(db)           
    features_collection = crud.get_features(db)  

    return templates.TemplateResponse(
        "admin.html",
        {
            "request": request,
            "stats": stats,
            "features": features_collection["features"]
        }
    )


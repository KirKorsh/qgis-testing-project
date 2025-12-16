from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.crud import feature as crud
from app.schemas import feature as schemas
from app.database import SessionLocal

router = APIRouter()

# Зависимость для сессии
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/features")
def add_feature(feature: schemas.FeatureCreate, db: Session = Depends(get_db)):
    db_feature = crud.create_feature(db, feature.dict())
    return {"id": db_feature.id}

@router.get("/features")
def read_features(db: Session = Depends(get_db)):
    return crud.get_features(db)

@router.get("/stats")
def read_stats(db: Session = Depends(get_db)):
    return crud.get_stats(db)

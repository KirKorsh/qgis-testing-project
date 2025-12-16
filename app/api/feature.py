from fastapi import APIRouter, Depends, HTTPException
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

@router.delete("/features/{feature_id}")
def remove_feature(feature_id: int, db: Session = Depends(get_db)):
    success = crud.delete_feature(db, feature_id)
    if not success:
        raise HTTPException(status_code=404, detail="Feature not found")
    return {"status": "deleted", "id": feature_id}

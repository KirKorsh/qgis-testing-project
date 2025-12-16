from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from .database import SessionLocal, engine, Base
from . import models, crud, schemas

app = FastAPI()

Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/features")
def add_feature(feature: schemas.FeatureCreate, db: Session = Depends(get_db)):
    db_feature = crud.create_feature(db, feature.dict())
    return {"id": db_feature.id}

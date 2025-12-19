import json
import logging
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from app.crud import feature as crud
from app.schemas import feature as schemas
from app.dependencies import get_db
router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/features")
def add_feature(feature: schemas.FeatureCreate, db: Session = Depends(get_db)):
    # Валидация геометрии
    try:
        geom_dict = json.loads(feature.geom) if isinstance(feature.geom, str) else feature.geom
        if geom_dict.get("type") not in ["Point", "LineString", "Polygon"]:
            raise HTTPException(
                status_code=422,
                detail=f"Geometry type '{geom_dict.get('type')}' is not supported. Use 'Point', 'LineString' or 'Polygon'."
            )
    except (json.JSONDecodeError, AttributeError, TypeError) as e:
        logger.warning(f"Invalid GeoJSON received: {feature.geom}")
        raise HTTPException(status_code=422, detail="Invalid GeoJSON format")

    # Попытка сохранения в БД
    try:
        db_feature = crud.create_feature(db, feature.dict())
        db.commit()
        logger.info(f"Feature created with ID: {db_feature.id}")
        return {"id": db_feature.id}
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Database error while creating feature: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error during feature creation")
    except Exception as e:
        # На случай других неожиданных ошибок
        db.rollback()
        logger.critical(f"Unexpected error in add_feature: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")

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
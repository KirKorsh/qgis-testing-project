from sqlalchemy.orm import Session
from . import models
from geoalchemy2.shape import from_shape
from shapely.geometry import shape

def create_feature(db: Session, feature_data):
    geom_shape = shape(feature_data["geom"])
    db_feature = models.Feature(
        geom=from_shape(geom_shape, srid=4326),
        geom_type=feature_data["geom_type"]
    )
    db.add(db_feature)
    db.commit()
    db.refresh(db_feature)
    return db_feature

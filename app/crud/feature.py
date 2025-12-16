from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.feature import Feature
from geoalchemy2.shape import from_shape, to_shape
from shapely.geometry import shape

def create_feature(db: Session, feature_data):
    geom_shape = shape(feature_data["geom"])
    db_feature = Feature(
        geom=from_shape(geom_shape, srid=4326),
        geom_type=feature_data["geom_type"]
    )
    db.add(db_feature)
    db.commit()
    db.refresh(db_feature)
    return db_feature

def get_features(db: Session):
    features = db.query(Feature).all()
    result = []
    for f in features:
        geom_shape = to_shape(f.geom)
        result.append({
            "type": "Feature",
            "id": f.id,
            "geometry": geom_shape.__geo_interface__,
            "properties": {"geom_type": f.geom_type}
        })
    return {"type": "FeatureCollection", "features": result}

def get_stats(db: Session):
    counts = (
        db.query(Feature.geom_type, func.count(Feature.id))
        .group_by(Feature.geom_type)
        .all()
    )
    stats = {"Point": 0, "LineString": 0, "Polygon": 0}
    for geom_type, count in counts:
        stats[geom_type] = count
    return {k.lower() + "s": v for k, v in stats.items()}

def delete_feature(db: Session, feature_id: int):
    feature = db.query(Feature).filter(Feature.id == feature_id).first()
    if feature:
        db.delete(feature)
        db.commit()
        return True
    return False
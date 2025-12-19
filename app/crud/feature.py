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

print(" МОДУЛЬ: Модуль crud.feature загружен")
def get_features(db: Session):
    print("CRUD: Вызвана get_features")
    try:
        features = db.query(Feature).all()
        print(f"   Найдено объектов: {len(features)}")
        result = []
        for f in features:
            geom_shape = to_shape(f.geom)
            result.append({
                "type": "Feature",
                "id": f.id,
                "geometry": geom_shape.__geo_interface__,
                "properties": {"geom_type": f.geom_type}
        }) 
            pass
        print(" CRUD: get_features завершена успешно")
        return {"type": "FeatureCollection", "features": result}
    except Exception as e:
        print(f" CRUD: ОШИБКА в get_features: {e}")
        raise

def get_stats(db: Session):
    print(" CRUD: Вызвана get_stats")
    try:
        counts = (
            db.query(Feature.geom_type, func.count(Feature.id))
            .group_by(Feature.geom_type)
            .all()
        )
        print(f"   Результат запроса: {counts}")
        stats = {"Point": 0, "LineString": 0, "Polygon": 0}
        for geom_type, count in counts:
            stats[geom_type] = count
            print(" CRUD: get_stats завершена успешно")
        return {k.lower() + "s": v for k, v in stats.items()}
    except Exception as e:
            print(f" CRUD: ОШИБКА в get_stats: {e}")
            raise

def delete_feature(db: Session, feature_id: int):
    print(f" [DELETE] Начало удаления для feature_id={feature_id}")
    
    #  Пробуем найти объект
    print(f"   Выполняю запрос: db.query(Feature).filter(Feature.id == {feature_id}).first()")
    feature = db.query(Feature).filter(Feature.id == feature_id).first()
    
    if feature:
        print(f"   Объект НАЙДЕН! id={feature.id}, geom_type={feature.geom_type}")
        print(f"   Пробую db.delete(feature)...")
        try:
            db.delete(feature)
            print(f"   Пробую db.commit()...")
            db.commit()
            print(f"   Успешно удален из БД!")
            return True
        except Exception as e:
            print(f"   ОШИБКА при commit: {e}")
            db.rollback()  # откат при ошибке
            return False
    else:
        print(f"   Объект с id={feature_id} НЕ НАЙДЕН в БД.")
        print(f"   Список ID в таблице features: {[f.id for f in db.query(Feature.id).all()]}")
        return False
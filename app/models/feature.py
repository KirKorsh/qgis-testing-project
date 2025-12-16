from sqlalchemy import Column, Integer, String
from geoalchemy2 import Geometry
from app.database import Base

class Feature(Base):
    __tablename__ = "features"
    id = Column(Integer, primary_key=True)
    geom = Column(Geometry("GEOMETRY", srid=4326))
    geom_type = Column(String, nullable=False)

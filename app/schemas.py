from pydantic import BaseModel
from typing import Any

class FeatureCreate(BaseModel):
    geom: Any  # GeoJSON объект
    geom_type: str

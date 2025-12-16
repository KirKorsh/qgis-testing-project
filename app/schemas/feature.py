from pydantic import BaseModel
from typing import Any

class FeatureCreate(BaseModel):
    geom: Any
    geom_type: str

class FeatureOut(BaseModel):
    id: int
    geom: Any
    geom_type: str

    class Config:
        orm_mode = True

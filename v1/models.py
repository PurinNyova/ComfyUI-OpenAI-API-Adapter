# v1/models.py
from fastapi import APIRouter
from pydantic import BaseModel
from typing import List
import time
from config import config
router = APIRouter()

class Model(BaseModel):
    id: str
    object: str
    created: int
    owned_by: str

class ModelsList(BaseModel):
    object: str
    data: List[Model]

#this sends models
@router.get("/models", response_model=ModelsList)
async def list_models():
    models_list = []
    for m in config["models"]:
        models_list.append(Model(
            id=m["id"],
            object="model",
            created=int(time.time()),
            owned_by="OAIAdapter"
        ))
    return ModelsList(
        object="list",
        data=models_list
    )
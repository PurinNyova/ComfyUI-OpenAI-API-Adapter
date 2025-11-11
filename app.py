# app.py
import logging
import os
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from v1 import models as models_router
from v1 import images_generations as images_router

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="OpenAI Adapter COMFYUI", version="1.0.0")

# CORS for you people who use ext domain like me
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(models_router.router, prefix="/v1")
app.include_router(images_router.router, prefix="/v1")

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8001)
import logging

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from modules import *

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(api.router)
logging.basicConfig(level=logging.INFO)

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=10000, log_level="info")

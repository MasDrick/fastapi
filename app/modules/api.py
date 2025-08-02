import logging

import modules.constants as constants
import modules.functions as functions
import modules.classes as classes
import modules.database.query_api as database
import modules.api_generate as generate
import modules.api_chats as chats
import modules.api_favorite as favorite

from fastapi import APIRouter, HTTPException, Header
from typing import Optional

router = APIRouter(
    prefix="/api",
    tags=["api"]
)

router.include_router(generate.router)
router.include_router(chats.router)
router.include_router(favorite.router)

@router.get("/")
def read_root():
    return {"message": "Добро пожаловать на бекенд INSUGPT!"}
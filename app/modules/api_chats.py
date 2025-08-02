import modules.classes as classes
import modules.database.query_api as database

from fastapi import APIRouter, HTTPException, Header
from typing import Optional

router = APIRouter(
    prefix="/chats",
    tags=["chats"]
)

@router.get("/history", response_model=list[classes.HistoryResponse])
def get_history(
    limit: int = 5,
    offset: int = 0,
    chat_id: Optional[str] = Header(None)
) -> list[classes.HistoryResponse]:
    if not chat_id:
        raise HTTPException(status_code=400, detail="Требуется chat_id в заголовке")

    resp = database.get_prompt_by_user(chat_id, limit, offset)

    if resp is None or len(resp) == 0:
        raise HTTPException(status_code=400, detail="Здесь пусто.")

    response = []
    for i in resp:
        response.append(classes.HistoryResponse(
            id=i[0],
            chat_id=i[1],
            request_type=i[2],
            request_datetime=i[5],
            prompt=i[3],
            response=i[4]
        ))
    return response

@router.get("/")
def get_chats(
    user_id: Optional[str] = Header(None)
):
    if not user_id:
        raise HTTPException(status_code=400, detail="Требуется user_id в заголовке")

    resp = database.get_chats_by_user(user_id)
    
    return resp

@router.post("/add", response_model=classes.ChatResponse)
def add_chat(
    chat : classes.Chat,
    user_id: Optional[str] = Header(None)
) -> classes.ChatResponse:
    if not user_id:
        raise HTTPException(status_code=400, detail="Требуется user_id в заголовке")
    
    chat_id = database.create_chat(user_id, chat.chat_name, chat.chat_type)

    return classes.ChatResponse(
        id=chat_id,
        chat_name=chat.chat_name,
        chat_type=chat.chat_type
    )

@router.delete("/delete")
def del_chat(chat_id: Optional[str] = Header(None)) -> bool:
    if not chat_id:
        raise HTTPException(status_code=400, detail="Требуется chat_id в заголовке")

    isDel = database.delete_chat(chat_id)

    if not isDel:
        raise HTTPException(status_code=404, detail="Чат не найден или уже удален")

    return True
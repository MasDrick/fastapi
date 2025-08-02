from pydantic import BaseModel
from typing import Optional
import enum

class ChatType(str, enum.Enum):
    MIXED = 'mixed'
    TEXT = 'text'
    IMAGE = 'image'

class Prompt(BaseModel):
    model: str
    used_prompt: str

class Chat(BaseModel):
    chat_name: str
    chat_type: Optional[ChatType] = ChatType.MIXED

class ResponsePrompt(BaseModel):
    used_prompt: str
    response: str

class HistoryResponse(BaseModel):
    id: int
    chat_id: int
    request_type: str
    request_datetime: str
    prompt: str
    response: str

class ChatResponse(BaseModel):
    id: int
    chat_name: str
    chat_type: ChatType
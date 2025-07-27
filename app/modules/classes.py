from pydantic import BaseModel

class Prompt(BaseModel):
    model: str
    used_prompt: str

class ResponsePrompt(BaseModel):
    used_prompt: str
    response: str

class HistoryResponse(BaseModel):
    id: int
    user_id: int
    request_type: str
    request_datetime: str
    prompt: str
    response: str
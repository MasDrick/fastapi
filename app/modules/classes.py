from pydantic import BaseModel

class Prompt(BaseModel):
    model: str
    used_prompt: str

class ResponsePrompt(BaseModel):
    used_prompt: str
    response: str

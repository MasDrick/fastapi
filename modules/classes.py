from pydantic import BaseModel

class Prompt(BaseModel):
    model: str
    used_prompt: str
    smart: bool | None
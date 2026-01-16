from pydantic import BaseModel
from typing import Optional

class ChatRequest(BaseModel):
    message: str
    role: str  # parent or student
    student_id: Optional[int] = None # Used when the chatbot needs to fetch attendance, marks, etc.


class ChatResponse(BaseModel):
    reply: str

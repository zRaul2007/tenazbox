from pydantic import BaseModel
from datetime import datetime

class CardCreate(BaseModel):
    question: str
    answer: str

class CardResponse(BaseModel):
    id: int
    question: str
    answer: str
    next_review: datetime

    model_config = {
    "from_attributes": True
}

class ReviewInput(BaseModel):
    performance: str  # "easy", "hard", "wrong"
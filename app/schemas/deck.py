from pydantic import BaseModel

class DeckCreate(BaseModel):
    name: str

class DeckResponse(BaseModel):
    id: int
    name: str

    model_config = {
    "from_attributes": True
}
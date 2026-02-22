from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.schemas.deck import DeckCreate, DeckResponse
from app.models.deck import Deck
from app.models.user import User
from app.services.auth import get_current_user
from fastapi import HTTPException

router = APIRouter(prefix="/decks", tags=["Decks"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/", response_model=DeckResponse)
def create_deck(
    deck: DeckCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    new_deck = Deck(
        name=deck.name,
        user_id=current_user.id
    )

    db.add(new_deck)
    db.commit()
    db.refresh(new_deck)

    return new_deck

#Controle de acesso por propriedade, para garantir que os usuários só acessem seus próprios decks.
@router.get("/{deck_id}", response_model=DeckResponse)
def get_deck(
    deck_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    deck = db.query(Deck).filter(
        Deck.id == deck_id,
        Deck.user_id == current_user.id
    ).first()

    if not deck:
        raise HTTPException(status_code=404, detail="Deck não encontrado")

    return deck


#Escopo por usuário, para que cada usuário veja apenas seus decks.
@router.get("/", response_model=list[DeckResponse])
def list_decks(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    decks = db.query(Deck).filter(Deck.user_id == current_user.id).all()
    return decks
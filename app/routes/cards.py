from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.schemas.card import CardCreate, CardResponse
from app.models.card import Card
from app.models.deck import Deck
from app.models.user import User
from app.services.auth import get_current_user
from datetime import datetime
from datetime import timedelta
from app.schemas.card import ReviewInput

router = APIRouter(prefix="/decks/{deck_id}/cards", tags=["Cards"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/", response_model=CardResponse)
def create_card(
    deck_id: int,
    card: CardCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    deck = db.query(Deck).filter(
        Deck.id == deck_id,
        Deck.user_id == current_user.id
    ).first()

    if not deck:
        raise HTTPException(status_code=404, detail="Deck não encontrado")

    new_card = Card(
        question=card.question,
        answer=card.answer,
        deck_id=deck.id
    )

    db.add(new_card)
    db.commit()
    db.refresh(new_card)

    return new_card

#Buscar cards para revisar hoje.
@router.get("/review/today", response_model=list[CardResponse])
def get_cards_for_today(
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

    now = datetime.utcnow()

    cards = db.query(Card).filter(
        Card.deck_id == deck.id,
        Card.next_review <= now
    ).all()

    return cards

#Endpoint para registrar a revisão de um card e atualizar o intervalo de revisão
@router.post("/{card_id}/review")
def review_card(
    deck_id: int,
    card_id: int,
    review: ReviewInput,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    card = db.query(Card).join(Deck).filter(
        Card.id == card_id,
        Deck.id == deck_id,
        Deck.user_id == current_user.id
    ).first()

    if not card:
        raise HTTPException(status_code=404, detail="Card não encontrado")

    if review.performance == "easy":
        card.interval_days += 3
    elif review.performance == "hard":
        card.interval_days += 1
    elif review.performance == "wrong":
        card.interval_days = 1
    else:
        raise HTTPException(status_code=400, detail="Performance inválida")

    card.next_review = datetime.utcnow() + timedelta(days=card.interval_days)

    db.commit()

    return {
        "message": "Revisão registrada",
        "next_review": card.next_review,
        "interval_days": card.interval_days
    }
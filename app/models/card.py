from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base

class Card(Base):
    __tablename__ = "cards"

    id = Column(Integer, primary_key=True, index=True)
    question = Column(String)
    answer = Column(String)

    deck_id = Column(Integer, ForeignKey("decks.id"))

    next_review = Column(DateTime, default=datetime.utcnow)
    interval_days = Column(Integer, default=1)

    deck = relationship("Deck", backref="cards")
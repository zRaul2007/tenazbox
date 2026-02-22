from fastapi import FastAPI
from app.routes import users, decks, cards
#O venv é uma ferramenta para criar ambientes virtuais isolados para projetos Python.
from app.database import engine, Base
from app.models import user, deck, card

Base.metadata.create_all(bind=engine)

app = FastAPI()

app.include_router(cards.router)

app.include_router(users.router)

app.include_router(decks.router)

@app.get("/")
def root():
    return {"message": "TenazBox API rodando"}

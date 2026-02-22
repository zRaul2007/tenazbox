
# ---------------- IMPORTAÇÕES ----------------

# APIRouter cria um "mini aplicativo" de rotas.
# Pense como um setor dentro de uma empresa:
# existe o setor financeiro, o setor RH... aqui é o "setor usuários".
from fastapi import APIRouter, Depends

# Session é a conexão ativa com o banco.
# É como um telefone ligado diretamente com o banco de dados.
from sqlalchemy.orm import Session

# Esse é o "formulário" que o usuário preenche ao criar conta.
# Ele garante que email e senha venham corretamente.
from app.schemas.user import UserCreate

# Nossa fábrica de conexões com o banco
from app.database import SessionLocal

# O modelo User representa a tabela "users" dentro do banco
from app.models.user import User

# Função que transforma a senha em algo ilegível (criptografado)
from app.services.security import hash_password

from fastapi import HTTPException
from app.services.auth import create_access_token
from passlib.context import CryptContext
from app.services.auth import get_current_user

# Criamos o roteador: a área responsável por tudo relacionado a usuários
router = APIRouter()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# ---------------- CONEXÃO COM O BANCO ----------------

# Essa função cria e entrega uma conexão com o banco para cada requisição.
# IMPORTANTE:
# Cada pessoa que acessa o site precisa de uma conexão própria temporária.
# Quando termina, a conexão é fechada (igual encerrar uma ligação).
def get_db():
    db = SessionLocal()  # abre conexão
    try:
        yield db          # entrega a conexão para quem pediu
    finally:
        db.close()        # fecha a conexão quando termina


@router.post("/login")
def login(user: UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.email == user.email).first()

    if not db_user:
        raise HTTPException(status_code=400, detail="Email ou senha inválidos")

    if not pwd_context.verify(user.password, db_user.hashed_password):
        raise HTTPException(status_code=400, detail="Email ou senha inválidos")

    access_token = create_access_token(data={"sub": db_user.email})

    return {"access_token": access_token, "token_type": "bearer"}



# ---------------- CRIAR USUÁRIO ----------------

# @router.post("/users")
# significa:
# "quando alguém enviar dados para /users usando método POST,
# execute a função abaixo"

@router.post("/users")
def create_user(user: UserCreate, db: Session = Depends(get_db)):

    # user: UserCreate
    # O FastAPI automaticamente:
    # 1) recebe o JSON enviado
    # 2) valida
    # 3) transforma em objeto Python

    # db: Session = Depends(get_db)
    # Aqui o FastAPI:
    # chama get_db()
    # pega uma conexão com o banco
    # entrega pra função automaticamente


    # -------- PASSO 1: PROTEGER A SENHA --------
    # Nunca guardamos senha original no banco.
    # Analogia:
    # você não guarda a chave da sua casa na porta,
    # você guarda um molde impossível de reconstruir.
    hashed = hash_password(user.password)


    # -------- PASSO 2: CRIAR OBJETO DO BANCO --------
    # Aqui criamos um "registro" de usuário em memória.
    # Ainda NÃO foi salvo no banco.
    db_user = User(
        email=user.email,
        hashed_password=hashed
    )


    # -------- PASSO 3: AVISAR O BANCO QUE EXISTE UM NOVO DADO --------
    # db.add = colocar na fila de coisas a serem salvas
    db.add(db_user)


    # -------- PASSO 4: SALVAR DE VERDADE --------
    # commit = apertar o botão "confirmar operação"
    # Sem isso, nada é gravado permanentemente.
    db.commit()


    # -------- PASSO 5: PEDIR O ID GERADO --------
    # O banco cria automaticamente o id (1, 2, 3...)
    # refresh atualiza o objeto com o valor real do banco
    db.refresh(db_user)


    # -------- RESPOSTA DA API --------
    # Isso é o que o usuário da API recebe de volta
    return {
        "id": db_user.id,
        "email": db_user.email
    }

@router.get("/me")
def read_users_me(current_user: User = Depends(get_current_user)):
    return {
        "id": current_user.id,
        "email": current_user.email
    }
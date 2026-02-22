# Biblioteca de datas (usada para colocar validade no token)
from datetime import datetime, timedelta
import os

# Biblioteca que cria e lê o JWT (o token de login)
from jose import JWTError, jwt

# Dependências do FastAPI
from fastapi import Depends, HTTPException

# Diz ao FastAPI que vamos usar autenticação via "Bearer Token"
from fastapi.security import OAuth2PasswordBearer

# Tipo da sessão do banco
from sqlalchemy.orm import Session

# Conexão com o banco
from app.database import SessionLocal

# Modelo da tabela de usuários
from app.models.user import User

# carregar o arquivo .env para pegar a chave secreta
from dotenv import load_dotenv


# Aqui o FastAPI entende:
# "Toda rota protegida vai esperar um token no header Authorization"
# Exemplo: Authorization: Bearer eyJhbGciOi...
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


# ---------- CONEXÃO COM BANCO ----------
def get_db():
    # cria conexão
    db = SessionLocal()
    try:
        # entrega a conexão para a rota usar
        yield db
    finally:
        # fecha conexão depois da requisição
        db.close()


# ---------- VERIFICAR USUÁRIO LOGADO ----------
def get_current_user(
    token: str = Depends(oauth2_scheme),  # pega automaticamente o token enviado
    db: Session = Depends(get_db)         # pega conexão com banco
):
    try:
        # decodifica o token usando a chave secreta
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

        # "sub" é o campo onde salvamos o email do usuário
        email: str = payload.get("sub")

        # se não existir email dentro do token → token inválido
        if email is None:
            raise HTTPException(status_code=401, detail="Token inválido")

    # se o token estiver alterado, vencido ou errado
    except JWTError:
        raise HTTPException(status_code=401, detail="Token inválido")

    # procura o usuário no banco usando o email do token
    user = db.query(User).filter(User.email == email).first()

    # se não achou → token até pode ser válido, mas usuário não existe
    if user is None:
        raise HTTPException(status_code=401, detail="Usuário não encontrado")

    # retorna o usuário para a rota que pediu autenticação
    return user

# lê as variáveis do .env ao iniciar
load_dotenv()

# ---------- CONFIGURAÇÕES DO TOKEN ----------
# chave secreta usada para "assinar" o token
# (quem não tem essa chave não consegue criar um token válido)
SECRET_KEY = os.getenv("SECRET_KEY")

# algoritmo de criptografia do JWT
ALGORITHM = "HS256"

# quanto tempo o login dura (minutos)
ACCESS_TOKEN_EXPIRE_MINUTES = 60


# ---------- CRIAR TOKEN DE LOGIN ----------
def create_access_token(data: dict):

    # copia os dados (ex: {"sub": email})
    to_encode = data.copy()

    # define data de expiração do login
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    # adiciona a validade dentro do token
    to_encode.update({"exp": expire})

    # cria o JWT assinado
    # resultado: string gigante codificada
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
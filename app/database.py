# biblioteca para acessar variáveis do sistema operacional
import os

# carrega automaticamente o conteúdo do arquivo .env
from dotenv import load_dotenv

# ferramentas do SQLAlchemy para conectar ao banco
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# lê o arquivo .env quando o servidor iniciar
load_dotenv()

# pega a variável DATABASE_URL definida no .env
# isso evita colocar usuário e senha direto no código (segurança)
DATABASE_URL = os.getenv("DATABASE_URL")

# cria a conexão com o banco PostgreSQL
# pool_pre_ping evita erro quando a conexão fica ociosa (muito comum em deploy)
engine = create_engine(DATABASE_URL, pool_pre_ping=True)

# cria sessões de comunicação com o banco
# cada requisição da API abre uma sessão e depois fecha
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# classe base que todos os modelos (tabelas) vão herdar
# é assim que o SQLAlchemy sabe quais tabelas criar
Base = declarative_base()
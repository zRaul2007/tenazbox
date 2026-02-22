
# Importamos uma ferramenta pronta especializada em segurança de senha
# (você NÃO deve tentar criar criptografia própria — isso quase sempre dá errado)
from passlib.context import CryptContext


# Aqui criamos o "método oficial" que o sistema usará para proteger senhas.
# schemes=["bcrypt"] → estamos escolhendo o tipo de criptografia
# deprecated="auto" → se no futuro existir um método melhor,
# a biblioteca automaticamente atualiza a proteção
pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto"
)


# Função responsável por transformar a senha digitada pelo usuário
# em algo impossível de reverter.
def hash_password(password: str):

    # IMPORTANTE:
    # Isso NÃO é apenas embaralhar texto.
    # O bcrypt:
    # 1) adiciona um "sal" (salt) aleatório
    # 2) executa milhares de cálculos
    # 3) gera um código impossível de reconstruir
    #
    # Analogia:
    # você não está escondendo a senha,
    # você está derretendo ela e moldando em uma chave irreversível.
    return pwd_context.hash(password)


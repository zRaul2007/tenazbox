from pydantic import BaseModel, EmailStr 
#O BaseModel realiza validação automática dos dados com base nos tipos definidos
class UserCreate(BaseModel):
    email: EmailStr #Obriga a escrever um email válido.
    password: str
    
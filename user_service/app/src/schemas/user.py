from pydantic import BaseModel

class LoginBase(BaseModel):
    user_name:str
    password:str


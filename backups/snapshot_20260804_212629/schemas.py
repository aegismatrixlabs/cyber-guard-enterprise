from pydantic import BaseModel

class UserLogin(BaseModel):
    username: str
    password: str

class AssetCreate(BaseModel):
    url: str

class Token(BaseModel):
    access_token: str
    token_type: str

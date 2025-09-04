from pydantic import BaseModel


class Token(BaseModel):
    access_token: str
    token_type: str
    expires_in: int  # seconds until expiration


class User(BaseModel):
    username: str

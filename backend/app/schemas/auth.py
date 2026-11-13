
from pydantic import BaseModel, Field


class LoginRequest(BaseModel):
    email: str = Field(pattern=r"^[^@\s]+@[^@\s]+$")
    password: str
    organization_code: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"

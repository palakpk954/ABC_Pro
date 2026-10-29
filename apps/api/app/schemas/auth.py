from typing import Optional
from pydantic import BaseModel, EmailStr, ConfigDict


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    org_id: str
    role: str
    user_id: str
    full_name: str


class TokenPayload(BaseModel):
    sub: Optional[str] = None
    org_id: Optional[str] = None
    role: Optional[str] = None


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    org_id: str
    email: str
    full_name: str
    role: str
    is_active: bool

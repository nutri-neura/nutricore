from pydantic import BaseModel, EmailStr, Field

from app.schemas.user import UserSummary


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in_seconds: int
    user: UserSummary

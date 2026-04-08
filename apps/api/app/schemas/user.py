from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr

from app.models.user import UserRole


class UserSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    full_name: str
    email: EmailStr
    role: UserRole
    is_active: bool
    created_at: datetime

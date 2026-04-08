from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, require_admin
from app.db.session import get_db
from app.models.user import User
from app.repositories.user import list_users
from app.schemas.user import UserSummary

router = APIRouter()


@router.get("/me", response_model=UserSummary)
def read_current_user(current_user: User = Depends(get_current_user)) -> UserSummary:
    return UserSummary.model_validate(current_user)


@router.get("", response_model=list[UserSummary])
def read_users(
    _: User = Depends(require_admin),
    db: Session = Depends(get_db),
) -> list[UserSummary]:
    return [UserSummary.model_validate(user) for user in list_users(db)]

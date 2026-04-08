from sqlalchemy.orm import Session

from app.core.security import IssuedToken, create_access_token, verify_password
from app.models.user import User
from app.repositories.user import get_user_by_email


def authenticate_user(db: Session, email: str, password: str) -> User | None:
    user = get_user_by_email(db, email)
    if user is None or not verify_password(password, user.password_hash):
        return None
    return user


def issue_access_token(user: User) -> IssuedToken:
    return create_access_token(str(user.id))

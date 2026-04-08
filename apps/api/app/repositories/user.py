from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.user import User, UserRole


def get_user_by_email(db: Session, email: str) -> User | None:
    return db.scalar(select(User).where(User.email == email.lower()))


def get_user_by_id(db: Session, user_id: int) -> User | None:
    return db.get(User, user_id)


def list_users(db: Session) -> list[User]:
    return list(db.scalars(select(User).order_by(User.created_at.asc())))


def create_user(
    db: Session,
    *,
    full_name: str,
    email: str,
    password_hash: str,
    role: UserRole,
) -> User:
    user = User(
        full_name=full_name,
        email=email.lower(),
        password_hash=password_hash,
        role=role,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

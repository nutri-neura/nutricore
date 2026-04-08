from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.security import hash_password
from app.models.user import UserRole
from app.repositories.user import create_user, get_user_by_email


def bootstrap_admin(db: Session) -> bool:
    settings = get_settings()
    if not settings.bootstrap_admin_enabled:
        return False

    existing_user = get_user_by_email(db, settings.bootstrap_admin_email)
    if existing_user is not None:
        return False

    create_user(
        db,
        full_name=settings.bootstrap_admin_name,
        email=settings.bootstrap_admin_email,
        password_hash=hash_password(settings.bootstrap_admin_password),
        role=UserRole.admin,
    )
    return True


def bootstrap_status() -> dict[str, bool | str]:
    settings = get_settings()
    return {
        "bootstrap_admin_enabled": settings.bootstrap_admin_enabled,
        "bootstrap_admin_email": settings.bootstrap_admin_email,
    }

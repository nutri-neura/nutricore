from dataclasses import dataclass
from datetime import UTC, datetime, timedelta

import jwt
from fastapi import HTTPException, status
from pwdlib import PasswordHash

from app.core.config import get_settings

password_hash = PasswordHash.recommended()


@dataclass(slots=True)
class IssuedToken:
    value: str
    expires_in_seconds: int


def hash_password(password: str) -> str:
    return password_hash.hash(password)


def verify_password(password: str, hashed_password: str) -> bool:
    return password_hash.verify(password, hashed_password)


def create_access_token(subject: str) -> IssuedToken:
    settings = get_settings()
    expires_in_seconds = settings.jwt_access_token_expire_minutes * 60
    expires_at = datetime.now(UTC) + timedelta(seconds=expires_in_seconds)
    payload = {
        "sub": subject,
        "exp": expires_at,
        "type": "access",
    }
    token = jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)
    return IssuedToken(value=token, expires_in_seconds=expires_in_seconds)


def decode_access_token(token: str) -> dict:
    settings = get_settings()
    try:
        return jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
    except jwt.PyJWTError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication token",
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc

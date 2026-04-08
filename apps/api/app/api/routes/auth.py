from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.auth import LoginRequest, TokenResponse
from app.schemas.user import UserSummary
from app.services.auth import authenticate_user, issue_access_token
from app.services.bootstrap import bootstrap_status

router = APIRouter()


@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)) -> TokenResponse:
    user = authenticate_user(db, payload.email, payload.password)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )

    token = issue_access_token(user)

    return TokenResponse(
        access_token=token.value,
        expires_in_seconds=token.expires_in_seconds,
        user=UserSummary.model_validate(user),
    )


@router.get("/bootstrap-status")
def get_bootstrap_status() -> dict[str, bool | str]:
    return bootstrap_status()

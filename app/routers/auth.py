from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
import jwt

from app.db.database import get_db
from app.models.user import User, UserRole
from app.models.refresh_token import RefreshToken
from app.schemas.user import (
    MessageResponse,
    RefreshTokenRequest,
    Token,
    UserCreate,
    UserResponse,
)
from app.core.rate_limit import enforce_auth_rate_limit
from app.core.security import (
    create_access_token,
    create_refresh_token,
    hash_password,
    hash_token_id,
    verify_password,
)
from app.core.config import settings

router = APIRouter(tags=["Auth"])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


def get_current_user(
    token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
    )

    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM],
        )

        email: str = payload.get("sub")
        if email is None or payload.get("type") != "access":
            raise credentials_exception

    except jwt.PyJWTError:
        raise credentials_exception

    user = db.query(User).filter(User.email == email).first()
    if user is None:
        raise credentials_exception
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user",
        )

    return user


def get_admin_user(current_user: User = Depends(get_current_user)):
    if current_user.role != UserRole.admin and not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required"
        )

    return current_user


@router.post("/register", response_model=UserResponse)
def register(
    user: UserCreate,
    db: Session = Depends(get_db),
    _: None = Depends(enforce_auth_rate_limit),
):

    existing_user = db.query(User).filter(User.email == user.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    new_user = User(
        email=user.email,
        hashed_password=hash_password(user.password),
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user


@router.post("/login", response_model=Token)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
    _: None = Depends(enforce_auth_rate_limit),
):
    db_user = db.query(User).filter(User.email == form_data.username).first()

    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials"
        )

    if not db_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user",
        )

    if not verify_password(form_data.password, db_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials"
        )

    return _issue_token_pair(db, db_user)


def _issue_token_pair(db: Session, user: User) -> dict[str, str]:
    claims = {"sub": user.email, "role": user.role.value}
    access_token = create_access_token(data=claims)
    refresh_token, token_id, expires_at = create_refresh_token(data=claims)
    db.add(
        RefreshToken(
            token_hash=hash_token_id(token_id),
            user_id=user.id,
            expires_at=expires_at.replace(tzinfo=None),
        )
    )
    db.commit()
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",  # nosec B105
    }


def _decode_refresh_token(token: str) -> dict:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or expired refresh token",
    )
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
    except jwt.PyJWTError:
        raise credentials_exception
    if (
        payload.get("type") != "refresh"
        or not payload.get("sub")
        or not payload.get("jti")
    ):
        raise credentials_exception
    return payload


@router.post("/refresh", response_model=Token)
def refresh_tokens(request: RefreshTokenRequest, db: Session = Depends(get_db)):
    payload = _decode_refresh_token(request.refresh_token)
    token_record = (
        db.query(RefreshToken)
        .filter(RefreshToken.token_hash == hash_token_id(payload["jti"]))
        .first()
    )
    now = datetime.now(timezone.utc).replace(tzinfo=None)
    if not token_record or token_record.revoked_at or token_record.expires_at <= now:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token",
        )
    user = db.query(User).filter(User.id == token_record.user_id).first()
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token",
        )
    token_record.revoked_at = now
    return _issue_token_pair(db, user)


@router.post("/logout", response_model=MessageResponse)
def logout(request: RefreshTokenRequest, db: Session = Depends(get_db)):
    payload = _decode_refresh_token(request.refresh_token)
    token_record = (
        db.query(RefreshToken)
        .filter(RefreshToken.token_hash == hash_token_id(payload["jti"]))
        .first()
    )
    if token_record and token_record.revoked_at is None:
        token_record.revoked_at = datetime.now(timezone.utc).replace(tzinfo=None)
        db.commit()
    return {"message": "Logged out"}

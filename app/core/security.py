from passlib.context import CryptContext
import hashlib
import uuid

import jwt
from datetime import datetime, timedelta, timezone
from app.core.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    if len(password.encode("utf-8")) > 72:
        raise ValueError("Password too long. Maximum 72 bytes.")
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str):
    return pwd_context.verify(plain_password, hashed_password)


def _create_token(data: dict, token_type: str, expires_delta: timedelta):
    to_encode = data.copy()
    now = datetime.now(timezone.utc)
    expire = now + expires_delta
    token_id = str(uuid.uuid4())
    to_encode.update({"exp": expire, "iat": now, "jti": token_id, "type": token_type})

    encoded = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded, token_id, expire


def create_access_token(data: dict) -> str:
    token, _, _ = _create_token(
        data,
        "access",
        timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
    )
    return token


def create_refresh_token(data: dict) -> tuple[str, str, datetime]:
    return _create_token(
        data,
        "refresh",
        timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
    )


def hash_token_id(token_id: str) -> str:
    return hashlib.sha256(token_id.encode("utf-8")).hexdigest()

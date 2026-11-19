import hashlib
import hmac
import os
from datetime import datetime, timedelta, timezone

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app import config
from app.database import get_db
from app.models import User

ITERATIONS = 200_000
bearer = HTTPBearer(auto_error=False)


def hash_password(password: str) -> str:
    salt = os.urandom(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, ITERATIONS)
    return f"{salt.hex()}${digest.hex()}"


def verify_password(password: str, stored: str) -> bool:
    try:
        salt_hex, digest_hex = stored.split("$")
    except ValueError:
        return False
    digest = hashlib.pbkdf2_hmac("sha256", password.encode(), bytes.fromhex(salt_hex), ITERATIONS)
    return hmac.compare_digest(digest.hex(), digest_hex)


def create_token(user_id: int) -> str:
    exp = datetime.now(timezone.utc) + timedelta(minutes=config.TOKEN_EXPIRE_MINUTES)
    return jwt.encode({"sub": str(user_id), "exp": exp}, config.SECRET_KEY, algorithm="HS256")


def get_current_user(
    creds: HTTPAuthorizationCredentials | None = Depends(bearer),
    db: Session = Depends(get_db),
) -> User:
    unauthorized = HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid or missing token")
    if creds is None:
        raise unauthorized
    try:
        payload = jwt.decode(creds.credentials, config.SECRET_KEY, algorithms=["HS256"])
        user = db.get(User, int(payload["sub"]))
    except (jwt.PyJWTError, KeyError, ValueError):
        raise unauthorized
    if user is None:
        raise unauthorized
    return user

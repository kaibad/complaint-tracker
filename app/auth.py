"""Password hashing, login tokens and role checks."""
import hashlib
import hmac
import os
import secrets
from datetime import timedelta

from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.orm import Session

from . import models
from .database import get_db

TOKEN_LIFETIME = timedelta(hours=12)
_bearer = HTTPBearer(auto_error=False)


def hash_password(password: str) -> str:
    salt = secrets.token_bytes(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, 200_000)
    return f"{salt.hex()}${digest.hex()}"


def verify_password(password: str, stored: str) -> bool:
    salt_hex, digest_hex = stored.split("$")
    digest = hashlib.pbkdf2_hmac("sha256", password.encode(), bytes.fromhex(salt_hex), 200_000)
    return hmac.compare_digest(digest.hex(), digest_hex)


def _hash_token(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()


def create_token(db: Session, user: models.User) -> str:
    token = secrets.token_urlsafe(32)
    db.add(
        models.AuthToken(
            token_hash=_hash_token(token),
            user_id=user.id,
            expires_at=models.utcnow() + TOKEN_LIFETIME,
        )
    )
    db.commit()
    return token


def revoke_token(db: Session, token: str) -> None:
    row = db.scalar(select(models.AuthToken).where(models.AuthToken.token_hash == _hash_token(token)))
    if row:
        db.delete(row)
        db.commit()


def get_current_user(
    creds: HTTPAuthorizationCredentials | None = Depends(_bearer),
    db: Session = Depends(get_db),
) -> models.User:
    if creds is None:
        raise HTTPException(status_code=401, detail="Not authenticated")
    row = db.scalar(
        select(models.AuthToken).where(models.AuthToken.token_hash == _hash_token(creds.credentials))
    )
    if row is None:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    expires = row.expires_at
    if expires.tzinfo is None:  # SQLite returns naive datetimes
        expires = expires.replace(tzinfo=models.utcnow().tzinfo)
    if expires < models.utcnow():
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    user = db.get(models.User, row.user_id)
    if user is None:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    return user


def require_admin(user: models.User = Depends(get_current_user)) -> models.User:
    if user.role != models.Role.ADMIN:
        raise HTTPException(status_code=403, detail="Admin access required")
    return user


def ensure_admin(db: Session) -> None:
    """Create the first admin account if none exists (credentials come from env vars)."""
    if db.scalar(select(models.User).where(models.User.role == models.Role.ADMIN)):
        return
    username = os.getenv("ADMIN_USERNAME", "admin")
    password = os.getenv("ADMIN_PASSWORD", "admin123")
    db.add(models.User(username=username, password_hash=hash_password(password), role=models.Role.ADMIN))
    db.commit()
    if "ADMIN_PASSWORD" not in os.environ:
        print(f"[WARNING] Created default admin '{username}' with password 'admin123'. "
              "Set ADMIN_USERNAME / ADMIN_PASSWORD before deploying.")

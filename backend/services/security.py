import hashlib
import os
import secrets
from datetime import datetime, timedelta
from typing import Any, Dict, Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt

try:
    from ..database.mongodb import users_collection, refresh_tokens_collection
except (ModuleNotFoundError, ImportError):
    from database.mongodb import users_collection, refresh_tokens_collection


SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "7"))

bearer_scheme = HTTPBearer(auto_error=False)


class AuthUser(Dict[str, Any]):
    pass


def _utcnow() -> datetime:
    return datetime.utcnow()


def canonical_email(email: str) -> str:
    return (email or "").strip().lower()


def create_access_token(email: str, role: str, mfa_verified: bool = False) -> str:
    expire = _utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = {
        "sub": canonical_email(email),
        "role": role,
        "mfa": bool(mfa_verified),
        "exp": expire,
        "type": "access",
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def issue_refresh_token(email: str, role: str) -> str:
    token = secrets.token_urlsafe(48)
    token_hash = hashlib.sha256(token.encode("utf-8")).hexdigest()
    refresh_tokens_collection.insert_one(
        {
            "token_hash": token_hash,
            "email": canonical_email(email),
            "role": role,
            "revoked": False,
            "created_at": _utcnow(),
            "expires_at": _utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS),
        }
    )
    return token


def revoke_refresh_token(token: str) -> None:
    token_hash = hashlib.sha256(token.encode("utf-8")).hexdigest()
    refresh_tokens_collection.update_one(
        {"token_hash": token_hash}, {"$set": {"revoked": True, "revoked_at": _utcnow()}}
    )


def refresh_session(refresh_token: str) -> Dict[str, str]:
    token_hash = hashlib.sha256(refresh_token.encode("utf-8")).hexdigest()
    record = refresh_tokens_collection.find_one({"token_hash": token_hash})

    if not record:
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    if record.get("revoked"):
        raise HTTPException(status_code=401, detail="Refresh token revoked")

    if record.get("expires_at") and record["expires_at"] < _utcnow():
        raise HTTPException(status_code=401, detail="Refresh token expired")

    user = users_collection.find_one({"email": record["email"]})
    if not user:
        raise HTTPException(status_code=401, detail="User not found")

    access_token = create_access_token(record["email"], record.get("role", user.get("user_type", "applicant")))
    new_refresh_token = issue_refresh_token(record["email"], record.get("role", user.get("user_type", "applicant")))
    revoke_refresh_token(refresh_token)
    return {"access_token": access_token, "refresh_token": new_refresh_token, "token_type": "bearer"}


def decode_access_token(token: str) -> Dict[str, Any]:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        if payload.get("type") != "access":
            raise HTTPException(status_code=401, detail="Invalid token type")
        return payload
    except JWTError as exc:
        raise HTTPException(status_code=401, detail="Invalid token") from exc


def get_current_user(credentials: Optional[HTTPAuthorizationCredentials] = Depends(bearer_scheme)) -> AuthUser:
    if not credentials or credentials.scheme.lower() != "bearer":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")

    payload = decode_access_token(credentials.credentials)
    email = canonical_email(payload.get("sub", ""))
    user = users_collection.find_one({"email": email})

    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")

    if not user.get("is_active", True):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User disabled")

    return AuthUser(
        {
            "email": user["email"],
            "full_name": user.get("full_name", ""),
            "role": user.get("user_type", "applicant"),
            "mfa_enabled": bool(user.get("mfa_enabled", False)),
            "mfa_verified": bool(payload.get("mfa", False)),
        }
    )


def require_roles(*roles: str):
    allowed = {r.strip().lower() for r in roles}

    def dependency(current_user: AuthUser = Depends(get_current_user)) -> AuthUser:
        role = str(current_user.get("role", "")).lower()
        if role not in allowed:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient role")
        return current_user

    return dependency


from datetime import datetime, timedelta
import os
import secrets

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from passlib.context import CryptContext

try:
    import bcrypt as bcrypt_lib
except Exception:
    bcrypt_lib = None

try:
    from ..database.mongodb import (
        users_collection,
        otp_codes_collection,
        password_reset_tokens_collection,
        signup_verifications_collection,
    )
    from ..services.audit_log import log_audit_event
    from ..services.email_service import send_email
    from ..services.email_templates import build_otp_email, build_password_reset_email
    from ..services.security import (
        canonical_email,
        create_access_token,
        issue_refresh_token,
        refresh_session,
        revoke_refresh_token,
    )
except (ModuleNotFoundError, ImportError):
    from database.mongodb import (
        users_collection,
        otp_codes_collection,
        password_reset_tokens_collection,
        signup_verifications_collection,
    )
    from services.audit_log import log_audit_event
    from services.email_service import send_email
    from services.email_templates import build_otp_email, build_password_reset_email
    from services.security import (
        canonical_email,
        create_access_token,
        issue_refresh_token,
        refresh_session,
        revoke_refresh_token,
    )

router = APIRouter()

# Use pbkdf2_sha256 to avoid passlib+bcrypt backend incompatibilities on newer bcrypt builds.
pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")
OTP_EXPIRE_MINUTES = int(os.getenv("OTP_EXPIRE_MINUTES", "5"))
RESET_TOKEN_EXPIRE_MINUTES = int(os.getenv("RESET_TOKEN_EXPIRE_MINUTES", "15"))
DEBUG_SHOW_OTP = os.getenv("DEBUG_SHOW_OTP", "false").lower() == "true"

ALLOWED_ROLES = {
    "applicant",
    "underwriter",
    "risk_manager",
    "admin",
    "auditor",
    "student",
    "unemployed",
}

class UserRegister(BaseModel):
    email: str = Field(...,)
    password: str
    full_name: str
    user_type: str
    phone: str = ""

class UserLogin(BaseModel):
    email: str
    password: str
    mfa_code: str | None = None


class RefreshRequest(BaseModel):
    refresh_token: str


class LogoutRequest(BaseModel):
    refresh_token: str


class OTPRequest(BaseModel):
    email: str
    purpose: str = "login"


class OTPVerifyRequest(BaseModel):
    email: str
    code: str
    purpose: str = "login"


class PasswordResetRequest(BaseModel):
    email: str


class PasswordResetConfirm(BaseModel):
    token: str
    new_password: str


class MFAConfigRequest(BaseModel):
    email: str
    enable: bool = True


class SignupOTPRequest(BaseModel):
    email: str


class SignupOTPVerifyRequest(BaseModel):
    email: str
    code: str


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, stored_password: str) -> bool:
    # Preferred scheme for new passwords.
    if stored_password.startswith("$pbkdf2-sha256$"):
        return pwd_context.verify(plain_password, stored_password)

    # Legacy bcrypt hashes from older deployments.
    if stored_password.startswith("$2") and bcrypt_lib is not None:
        try:
            return bcrypt_lib.checkpw(
                plain_password.encode("utf-8"),
                stored_password.encode("utf-8"),
            )
        except Exception:
            return False

    # Support old plaintext records during migration.
    return plain_password == stored_password


def _generate_otp_code() -> str:
    return f"{secrets.randbelow(1_000_000):06d}"


def _store_otp(email: str, purpose: str) -> str:
    code = _generate_otp_code()
    otp_codes_collection.insert_one(
        {
            "email": canonical_email(email),
            "purpose": purpose,
            "code": code,
            "verified": False,
            "created_at": datetime.utcnow(),
            "expires_at": datetime.utcnow() + timedelta(minutes=OTP_EXPIRE_MINUTES),
        }
    )
    return code


def _store_signup_otp(email: str) -> str:
    code = _generate_otp_code()
    signup_verifications_collection.insert_one(
        {
            "email": canonical_email(email),
            "code": code,
            "verified": False,
            "created_at": datetime.utcnow(),
            "expires_at": datetime.utcnow() + timedelta(minutes=OTP_EXPIRE_MINUTES),
        }
    )
    return code


def _verify_otp(email: str, code: str, purpose: str) -> bool:
    record = otp_codes_collection.find_one(
        {
            "email": canonical_email(email),
            "purpose": purpose,
            "code": code,
            "verified": False,
            "expires_at": {"$gt": datetime.utcnow()},
        },
        sort=[("created_at", -1)],
    )

    if not record:
        return False

    otp_codes_collection.update_one({"_id": record["_id"]}, {"$set": {"verified": True, "verified_at": datetime.utcnow()}})
    return True


def _verify_signup_otp(email: str, code: str) -> bool:
    record = signup_verifications_collection.find_one(
        {
            "email": canonical_email(email),
            "code": code,
            "verified": False,
            "expires_at": {"$gt": datetime.utcnow()},
        },
        sort=[("created_at", -1)],
    )
    if not record:
        return False

    signup_verifications_collection.update_one(
        {"_id": record["_id"]}, {"$set": {"verified": True, "verified_at": datetime.utcnow()}}
    )
    return True


@router.post("/signup/request-otp")
async def signup_request_otp(payload: SignupOTPRequest):
    user_email = canonical_email(payload.email)
    if users_collection.find_one({"email": user_email}):
        raise HTTPException(status_code=400, detail="Email already registered")

    code = _store_signup_otp(user_email)
    template = build_otp_email(
        applicant_name="Applicant",
        otp_code=code,
        purpose="signup verification",
        expiry_minutes=OTP_EXPIRE_MINUTES,
    )
    sent = send_email(user_email, template["subject"], template["text"], html_body=template["html"])
    if not sent:
        raise HTTPException(status_code=503, detail="Email service not configured. Contact support.")

    response = {
        "message": "Signup OTP sent to your email",
        "expires_in_minutes": OTP_EXPIRE_MINUTES,
    }
    if DEBUG_SHOW_OTP:
        response["debug_otp"] = code
    return response


@router.post("/signup/verify-otp")
async def signup_verify_otp(payload: SignupOTPVerifyRequest):
    user_email = canonical_email(payload.email)
    valid = _verify_signup_otp(user_email, payload.code)
    if not valid:
        raise HTTPException(status_code=400, detail="Invalid or expired signup OTP")

    return {"message": "Email verified. You can now complete registration."}

@router.post("/register")
async def register(user: UserRegister):
    user_email = canonical_email(user.email)
    # Check if user exists
    if users_collection.find_one({"email": user_email}):
        raise HTTPException(status_code=400, detail="Email already registered")

    verified_signup = signup_verifications_collection.find_one(
        {
            "email": user_email,
            "verified": True,
            "expires_at": {"$gt": datetime.utcnow()},
        },
        sort=[("created_at", -1)],
    )
    if not verified_signup:
        raise HTTPException(status_code=400, detail="Verify email OTP before registration")
    
    role = user.user_type.strip().lower()
    if role not in ALLOWED_ROLES:
        raise HTTPException(status_code=400, detail="Invalid user_type")

    hashed_password = hash_password(user.password)
    
    # Create user document
    user_doc = {
        "email": user_email,
        "password": hashed_password,
        "full_name": user.full_name,
        "user_type": role,
        "phone": user.phone,
        "created_at": datetime.utcnow(),
        "is_active": True,
        "email_verified": True,
        "mfa_enabled": False,
    }
    
    result = users_collection.insert_one(user_doc)
    
    log_audit_event(
        action="auth.register",
        actor_email=user_email,
        actor_role=role,
        entity_type="user",
        entity_id=str(result.inserted_id),
        metadata={"email": user_email},
    )

    signup_verifications_collection.delete_many({"email": user_email})

    return {
        "message": "User registered successfully",
        "user_id": str(result.inserted_id),
        "email": user_email
    }

@router.post("/login")
async def login(user: UserLogin):
    user_email = canonical_email(user.email)
    # Find user
    db_user = users_collection.find_one({"email": user_email})
    
    if not db_user:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    password_ok = verify_password(user.password, db_user["password"])
    if not password_ok:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    # Auto-migrate legacy bcrypt/plaintext passwords to pbkdf2_sha256.
    if not str(db_user.get("password", "")).startswith("$pbkdf2-sha256$"):
        users_collection.update_one(
            {"email": user_email},
            {
                "$set": {
                    "password": hash_password(user.password),
                    "password_migrated_at": datetime.utcnow(),
                }
            },
        )

    if not db_user.get("email_verified", False):
        raise HTTPException(status_code=403, detail="Email not verified")

    if db_user.get("mfa_enabled"):
        if not user.mfa_code:
            raise HTTPException(status_code=403, detail="MFA_REQUIRED")
        if not _verify_otp(user_email, user.mfa_code, "mfa_login"):
            raise HTTPException(status_code=401, detail="Invalid MFA code")
    
    # Create access token
    access_token = create_access_token(user_email, db_user["user_type"], mfa_verified=bool(db_user.get("mfa_enabled")))
    refresh_token = issue_refresh_token(user_email, db_user["user_type"])

    log_audit_event(
        action="auth.login",
        actor_email=user_email,
        actor_role=db_user["user_type"],
        entity_type="user",
        entity_id=str(db_user.get("_id", user_email)),
        metadata={"mfa_enabled": bool(db_user.get("mfa_enabled"))},
    )
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "user_type": db_user["user_type"],
        "full_name": db_user["full_name"],
        "email": db_user["email"]
    }


@router.post("/refresh")
async def refresh_token(request: RefreshRequest):
    session = refresh_session(request.refresh_token)
    return session


@router.post("/logout")
async def logout(request: LogoutRequest):
    revoke_refresh_token(request.refresh_token)
    return {"message": "Logged out"}


@router.post("/otp/request")
async def request_otp(request: OTPRequest):
    user_email = canonical_email(request.email)
    db_user = users_collection.find_one({"email": user_email})
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    if not db_user.get("email_verified", False):
        raise HTTPException(status_code=403, detail="Email not verified")

    code = _store_otp(user_email, request.purpose)
    template = build_otp_email(
        applicant_name=str(db_user.get("full_name", "Customer")),
        otp_code=code,
        purpose=request.purpose,
        expiry_minutes=OTP_EXPIRE_MINUTES,
    )
    sent = send_email(user_email, template["subject"], template["text"], html_body=template["html"])
    if not sent:
        raise HTTPException(status_code=503, detail="Email service not configured. Contact support.")
    payload = {
        "message": f"OTP generated for {request.purpose}",
        "expires_in_minutes": OTP_EXPIRE_MINUTES,
    }
    if DEBUG_SHOW_OTP:
        payload["debug_otp"] = code

    log_audit_event(
        action="auth.otp.request",
        actor_email=user_email,
        actor_role=db_user.get("user_type", "applicant"),
        entity_type="otp",
        entity_id=user_email,
        metadata={"purpose": request.purpose},
    )
    return payload


@router.post("/otp/verify")
async def verify_otp(request: OTPVerifyRequest):
    user_email = canonical_email(request.email)
    valid = _verify_otp(user_email, request.code, request.purpose)
    if not valid:
        raise HTTPException(status_code=400, detail="Invalid or expired OTP")

    db_user = users_collection.find_one({"email": user_email})
    role = db_user.get("user_type", "applicant") if db_user else "applicant"
    log_audit_event(
        action="auth.otp.verify",
        actor_email=user_email,
        actor_role=role,
        entity_type="otp",
        entity_id=user_email,
        metadata={"purpose": request.purpose},
    )
    return {"message": "OTP verified"}


@router.post("/password-reset/request")
async def password_reset_request(payload: PasswordResetRequest):
    user_email = canonical_email(payload.email)
    user = users_collection.find_one({"email": user_email})
    if not user:
        # Avoid user enumeration by returning success.
        return {"message": "If account exists, reset instructions are sent"}

    if not user.get("email_verified", False):
        return {"message": "If account exists, reset instructions are sent"}

    token = secrets.token_urlsafe(32)
    password_reset_tokens_collection.insert_one(
        {
            "email": user_email,
            "token": token,
            "used": False,
            "created_at": datetime.utcnow(),
            "expires_at": datetime.utcnow() + timedelta(minutes=RESET_TOKEN_EXPIRE_MINUTES),
        }
    )

    template = build_password_reset_email(
        applicant_name=str(user.get("full_name", "Customer")),
        reset_token=token,
        expiry_minutes=RESET_TOKEN_EXPIRE_MINUTES,
    )
    sent = send_email(user_email, template["subject"], template["text"], html_body=template["html"])
    if not sent:
        raise HTTPException(status_code=503, detail="Email service not configured. Contact support.")

    result = {"message": "Reset token generated", "expires_in_minutes": RESET_TOKEN_EXPIRE_MINUTES}
    if DEBUG_SHOW_OTP:
        result["debug_reset_token"] = token
    return result


@router.post("/password-reset/confirm")
async def password_reset_confirm(payload: PasswordResetConfirm):
    token_record = password_reset_tokens_collection.find_one(
        {
            "token": payload.token,
            "used": False,
            "expires_at": {"$gt": datetime.utcnow()},
        }
    )
    if not token_record:
        raise HTTPException(status_code=400, detail="Invalid or expired reset token")

    users_collection.update_one(
        {"email": token_record["email"]},
        {"$set": {"password": hash_password(payload.new_password), "password_updated_at": datetime.utcnow()}},
    )
    password_reset_tokens_collection.update_one(
        {"_id": token_record["_id"]}, {"$set": {"used": True, "used_at": datetime.utcnow()}}
    )

    return {"message": "Password updated successfully"}


@router.post("/mfa/config")
async def mfa_config(payload: MFAConfigRequest):
    user_email = canonical_email(payload.email)
    user = users_collection.find_one({"email": user_email})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    users_collection.update_one({"email": user_email}, {"$set": {"mfa_enabled": payload.enable}})
    log_audit_event(
        action="auth.mfa.config",
        actor_email=user_email,
        actor_role=user.get("user_type", "applicant"),
        entity_type="user",
        entity_id=str(user.get("_id", user_email)),
        metadata={"enabled": payload.enable},
    )
    return {"message": f"MFA {'enabled' if payload.enable else 'disabled'}"}


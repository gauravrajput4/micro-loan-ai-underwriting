import os
import uuid
from datetime import datetime

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile

try:
    from ..database.mongodb import loan_applications_collection, users_collection
    from ..services.audit_log import log_audit_event
    from ..services.security import AuthUser, get_current_user
except (ModuleNotFoundError, ImportError):
    from database.mongodb import loan_applications_collection, users_collection
    from services.audit_log import log_audit_event
    from services.security import AuthUser, get_current_user


router = APIRouter()

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROFILE_UPLOAD_DIR = os.path.join(BASE_DIR, "uploads", "profile_pictures")
ALLOWED_CONTENT_TYPES = {"image/jpeg", "image/png", "image/webp"}
MAX_PROFILE_SIZE_BYTES = 3 * 1024 * 1024


os.makedirs(PROFILE_UPLOAD_DIR, exist_ok=True)


def _file_extension(content_type: str, filename: str) -> str:
    if content_type == "image/jpeg":
        return ".jpg"
    if content_type == "image/png":
        return ".png"
    if content_type == "image/webp":
        return ".webp"
    _, ext = os.path.splitext(filename or "")
    return ext.lower() if ext else ".jpg"


def _remove_old_picture(old_path: str | None) -> None:
    if not old_path:
        return
    try:
        if os.path.exists(old_path):
            os.remove(old_path)
    except OSError:
        pass


@router.get("/me")
async def get_my_profile(current_user: AuthUser = Depends(get_current_user)):
    email = current_user["email"]
    user = users_collection.find_one({"email": email}, {"password": 0})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    has_verified_kyc = (
        loan_applications_collection.count_documents(
            {
                "email": email,
                "kyc_status": "kyc_verified",
            },
            limit=1,
        )
        > 0
    )

    return {
        "email": user.get("email", ""),
        "full_name": user.get("full_name", ""),
        "phone": user.get("phone", ""),
        "user_type": user.get("user_type", "applicant"),
        "profile_image_url": user.get("profile_image_url", ""),
        "kyc_verified": has_verified_kyc,
        "created_at": user.get("created_at"),
    }


@router.post("/me/picture")
async def upload_profile_picture(
    file: UploadFile = File(...),
    current_user: AuthUser = Depends(get_current_user),
):
    if file.content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(status_code=400, detail="Only JPG, PNG, or WEBP images are allowed")

    content = await file.read()
    if len(content) > MAX_PROFILE_SIZE_BYTES:
        raise HTTPException(status_code=400, detail="Image too large (max 3MB)")

    extension = _file_extension(file.content_type or "", file.filename or "")
    filename = f"{uuid.uuid4().hex}{extension}"
    disk_path = os.path.join(PROFILE_UPLOAD_DIR, filename)

    with open(disk_path, "wb") as handle:
        handle.write(content)

    profile_url = f"/media/profile_pictures/{filename}"
    email = current_user["email"]
    user = users_collection.find_one({"email": email})
    old_path = user.get("profile_image_path") if user else None

    users_collection.update_one(
        {"email": email},
        {
            "$set": {
                "profile_image_url": profile_url,
                "profile_image_path": disk_path,
                "profile_image_updated_at": datetime.utcnow(),
            }
        },
    )

    _remove_old_picture(old_path)

    log_audit_event(
        action="profile.picture.updated",
        actor_email=email,
        actor_role=current_user.get("role", "applicant"),
        entity_type="user",
        entity_id=email,
        metadata={"profile_image_url": profile_url},
    )

    return {"message": "Profile picture uploaded", "profile_image_url": profile_url}


@router.delete("/me/picture")
async def delete_profile_picture(current_user: AuthUser = Depends(get_current_user)):
    email = current_user["email"]
    user = users_collection.find_one({"email": email})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    _remove_old_picture(user.get("profile_image_path"))

    users_collection.update_one(
        {"email": email},
        {
            "$set": {
                "profile_image_url": "",
                "profile_image_path": "",
                "profile_image_updated_at": datetime.utcnow(),
            }
        },
    )

    log_audit_event(
        action="profile.picture.deleted",
        actor_email=email,
        actor_role=current_user.get("role", "applicant"),
        entity_type="user",
        entity_id=email,
        metadata={},
    )

    return {"message": "Profile picture removed"}


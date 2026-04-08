from datetime import datetime
from typing import Optional

from bson import ObjectId
from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from pydantic import BaseModel

try:
    from ..database.mongodb import kyc_documents_collection, loan_applications_collection
    from ..services.audit_log import log_audit_event
    from ..services.kyc_engine import (
        KYCValidationError,
        mock_liveness_check,
        mock_ocr_extract,
        validate_document_number,
    )
    from ..services.security import AuthUser, get_current_user, require_roles
except (ModuleNotFoundError, ImportError):
    from database.mongodb import kyc_documents_collection, loan_applications_collection
    from services.audit_log import log_audit_event
    from services.kyc_engine import (
        KYCValidationError,
        mock_liveness_check,
        mock_ocr_extract,
        validate_document_number,
    )
    from services.security import AuthUser, get_current_user, require_roles


router = APIRouter()


class LivenessRequest(BaseModel):
    blink_score: float
    face_match_score: float


class KYCReviewRequest(BaseModel):
    status: str
    notes: Optional[str] = None


@router.post("/documents")
async def upload_kyc_document(
    loan_id: str = Form(...),
    doc_type: str = Form(...),
    doc_number: str = Form(...),
    file: UploadFile = File(...),
    current_user: AuthUser = Depends(get_current_user),
):
    role = current_user["role"].lower()
    if role not in {"applicant", "student", "unemployed", "admin"}:
        raise HTTPException(status_code=403, detail="Role cannot upload KYC")

    try:
        validate_document_number(doc_type.strip().lower(), doc_number)
    except KYCValidationError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    content = await file.read()
    if len(content) > 8 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="KYC file too large (max 8MB)")

    if not ObjectId.is_valid(loan_id):
        raise HTTPException(status_code=400, detail="Invalid loan_id")

    ocr_data = mock_ocr_extract(file.filename, doc_number)
    kyc_documents_collection.insert_one(
        {
            "loan_id": loan_id,
            "email": current_user["email"],
            "doc_type": doc_type.strip().lower(),
            "doc_number": doc_number.strip().upper(),
            "file_name": file.filename,
            "ocr": ocr_data,
            "created_at": datetime.utcnow(),
            "status": "document_uploaded",
        }
    )

    loan_applications_collection.update_one(
        {"_id": ObjectId(loan_id)},
        {
            "$set": {
                "kyc_status": "document_uploaded",
                "updated_at": datetime.utcnow(),
                "status": "under_review",
            }
        },
    )

    log_audit_event(
        action="kyc.document.uploaded",
        actor_email=current_user["email"],
        actor_role=current_user["role"],
        entity_type="loan",
        entity_id=loan_id,
        metadata={"doc_type": doc_type},
    )

    return {"message": "KYC document uploaded", "ocr": ocr_data}


@router.post("/selfie")
async def upload_selfie(
    loan_id: str = Form(...),
    file: UploadFile = File(...),
    current_user: AuthUser = Depends(get_current_user),
):
    if not ObjectId.is_valid(loan_id):
        raise HTTPException(status_code=400, detail="Invalid loan_id")

    content = await file.read()
    if len(content) > 5 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="Selfie file too large (max 5MB)")

    kyc_documents_collection.insert_one(
        {
            "loan_id": loan_id,
            "email": current_user["email"],
            "doc_type": "selfie",
            "file_name": file.filename,
            "created_at": datetime.utcnow(),
            "status": "selfie_uploaded",
        }
    )

    loan_applications_collection.update_one(
        {"_id": ObjectId(loan_id)},
        {"$set": {"kyc_status": "selfie_uploaded", "updated_at": datetime.utcnow()}},
    )

    log_audit_event(
        action="kyc.selfie.uploaded",
        actor_email=current_user["email"],
        actor_role=current_user["role"],
        entity_type="loan",
        entity_id=loan_id,
        metadata={"file_name": file.filename},
    )

    return {"message": "Selfie uploaded"}


@router.post("/liveness/verify")
async def verify_liveness(
    loan_id: str,
    request: LivenessRequest,
    current_user: AuthUser = Depends(get_current_user),
):
    if not ObjectId.is_valid(loan_id):
        raise HTTPException(status_code=400, detail="Invalid loan_id")

    result = mock_liveness_check(request.blink_score, request.face_match_score)
    passed = bool(result["passed"])

    status = "kyc_verified" if passed else "kyc_failed"
    loan_applications_collection.update_one(
        {"_id": ObjectId(loan_id)},
        {
            "$set": {
                "kyc_status": status,
                "liveness_result": result,
                "updated_at": datetime.utcnow(),
            }
        },
    )

    log_audit_event(
        action="kyc.liveness.verified",
        actor_email=current_user["email"],
        actor_role=current_user["role"],
        entity_type="loan",
        entity_id=loan_id,
        metadata={"passed": passed, "scores": result},
    )

    return {"message": "Liveness evaluated", "kyc_status": status, "result": result}


@router.get("/status/{loan_id}")
async def kyc_status(loan_id: str, current_user: AuthUser = Depends(get_current_user)):
    if not ObjectId.is_valid(loan_id):
        raise HTTPException(status_code=400, detail="Invalid loan_id")

    loan = loan_applications_collection.find_one({"_id": ObjectId(loan_id)})
    if not loan:
        raise HTTPException(status_code=404, detail="Loan not found")

    role = current_user["role"].lower()
    owner_email = str(loan.get("email", "")).strip().lower()
    if role in {"applicant", "student", "unemployed"} and owner_email != current_user["email"]:
        raise HTTPException(status_code=403, detail="Cannot view other user's KYC")

    docs = list(kyc_documents_collection.find({"loan_id": loan_id}).sort("created_at", -1))
    for d in docs:
        d["_id"] = str(d["_id"])

    return {
        "loan_id": loan_id,
        "kyc_status": loan.get("kyc_status", "not_started"),
        "documents": docs,
    }


@router.post("/review/{loan_id}")
async def review_kyc(
    loan_id: str,
    request: KYCReviewRequest,
    current_user: AuthUser = Depends(require_roles("underwriter", "risk_manager", "admin")),
):
    if not ObjectId.is_valid(loan_id):
        raise HTTPException(status_code=400, detail="Invalid loan_id")

    review_status = request.status.strip().lower()
    if review_status not in {"kyc_verified", "kyc_failed", "under_review"}:
        raise HTTPException(status_code=400, detail="Invalid review status")

    loan_applications_collection.update_one(
        {"_id": ObjectId(loan_id)},
        {
            "$set": {
                "kyc_status": review_status,
                "kyc_review_notes": request.notes or "",
                "kyc_reviewed_by": current_user["email"],
                "kyc_reviewed_at": datetime.utcnow(),
                "updated_at": datetime.utcnow(),
            }
        },
    )

    log_audit_event(
        action="kyc.reviewed",
        actor_email=current_user["email"],
        actor_role=current_user["role"],
        entity_type="loan",
        entity_id=loan_id,
        metadata={"status": review_status, "notes": request.notes or ""},
    )

    return {"message": "KYC review updated", "kyc_status": review_status}


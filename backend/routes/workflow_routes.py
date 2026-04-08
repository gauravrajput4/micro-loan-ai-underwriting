from datetime import datetime
from typing import Optional

from bson import ObjectId
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

try:
    from ..database.mongodb import loan_applications_collection, loan_predictions_collection
    from ..services.audit_log import log_audit_event
    from ..services.security import AuthUser, get_current_user, require_roles
    from ..services.email_service import send_email
    from ..services.email_templates import build_loan_decision_email
except (ModuleNotFoundError, ImportError):
    from database.mongodb import loan_applications_collection, loan_predictions_collection
    from services.audit_log import log_audit_event
    from services.security import AuthUser, get_current_user, require_roles
    from services.email_service import send_email
    from services.email_templates import build_loan_decision_email


router = APIRouter()


def _send_workflow_decision_email(
    *,
    to_email: str,
    applicant_name: str,
    decision: str,
    requested_amount: float,
    reasons: list[str],
    recommendations: list[str],
) -> None:
    content = build_loan_decision_email(
        decision=decision,
        applicant_name=applicant_name,
        requested_amount=requested_amount,
        reasons=reasons,
        recommendations=recommendations,
    )
    send_email(to_email, content["subject"], content["text"], html_body=content["html"])


class LifecycleTransitionRequest(BaseModel):
    to_status: str
    comment: Optional[str] = None


class DecisionRequest(BaseModel):
    decision: str = Field(..., description="approved or rejected")
    reason: str


class OverrideDecisionRequest(BaseModel):
    loan_id: str
    from_decision: str
    to_decision: str
    reason: str = Field(..., min_length=8)


ALLOWED_STATUSES = {
    "draft",
    "submitted",
    "under_review",
    "approved",
    "rejected",
    "disbursed",
    "closed",
    "defaulted",
}

ALLOWED_TRANSITIONS = {
    "draft": {"submitted"},
    "submitted": {"under_review", "rejected"},
    "under_review": {"approved", "rejected"},
    "approved": {"disbursed", "rejected"},
    "rejected": set(),
    "disbursed": {"closed", "defaulted"},
    "closed": set(),
    "defaulted": set(),
}


@router.get("/cases/my")
async def my_cases(current_user: AuthUser = Depends(get_current_user)):
    role = current_user["role"].lower()
    query = {} if role in {"underwriter", "risk_manager", "admin", "auditor"} else {"email": current_user["email"]}
    docs = list(loan_applications_collection.find(query).sort("created_at", -1).limit(100))
    for d in docs:
        d["_id"] = str(d["_id"])
    return {"cases": docs}


@router.post("/cases/{loan_id}/transition")
async def transition_case(
    loan_id: str,
    request: LifecycleTransitionRequest,
    current_user: AuthUser = Depends(require_roles("underwriter", "risk_manager", "admin")),
):
    if not ObjectId.is_valid(loan_id):
        raise HTTPException(status_code=400, detail="Invalid loan_id")

    case = loan_applications_collection.find_one({"_id": ObjectId(loan_id)})
    if not case:
        raise HTTPException(status_code=404, detail="Loan case not found")

    current_status = str(case.get("status", "draft")).lower()
    next_status = request.to_status.strip().lower()

    if next_status not in ALLOWED_STATUSES:
        raise HTTPException(status_code=400, detail="Unknown status")

    if next_status not in ALLOWED_TRANSITIONS.get(current_status, set()):
        raise HTTPException(status_code=400, detail=f"Invalid transition: {current_status} -> {next_status}")

    loan_applications_collection.update_one(
        {"_id": ObjectId(loan_id)},
        {
            "$set": {
                "status": next_status,
                "updated_at": datetime.utcnow(),
                "status_comment": request.comment or "",
                "status_updated_by": current_user["email"],
            }
        },
    )

    log_audit_event(
        action="loan.status.transition",
        actor_email=current_user["email"],
        actor_role=current_user["role"],
        entity_type="loan",
        entity_id=loan_id,
        metadata={"from": current_status, "to": next_status, "comment": request.comment or ""},
    )

    return {"message": "Loan status updated", "status": next_status}


@router.post("/cases/{loan_id}/decision")
async def set_decision(
    loan_id: str,
    request: DecisionRequest,
    current_user: AuthUser = Depends(require_roles("underwriter", "risk_manager", "admin")),
):
    if not ObjectId.is_valid(loan_id):
        raise HTTPException(status_code=400, detail="Invalid loan_id")

    case = loan_applications_collection.find_one({"_id": ObjectId(loan_id)})
    if not case:
        raise HTTPException(status_code=404, detail="Loan case not found")

    decision = request.decision.strip().lower()
    if decision not in {"approved", "rejected"}:
        raise HTTPException(status_code=400, detail="Decision must be approved or rejected")

    status = "approved" if decision == "approved" else "rejected"
    loan_applications_collection.update_one(
        {"_id": ObjectId(loan_id)},
        {
            "$set": {
                "status": status,
                "final_decision": decision,
                "decision_reason": request.reason,
                "decision_by": current_user["email"],
                "decision_at": datetime.utcnow(),
                "updated_at": datetime.utcnow(),
            }
        },
    )

    log_audit_event(
        action="loan.decision.finalized",
        actor_email=current_user["email"],
        actor_role=current_user["role"],
        entity_type="loan",
        entity_id=loan_id,
        metadata={"decision": decision, "reason": request.reason},
    )

    _send_workflow_decision_email(
        to_email=str(case.get("email", "")).strip().lower(),
        applicant_name=str(case.get("full_name", "Applicant")),
        decision=decision,
        requested_amount=float(case.get("loan_amount", 0) or 0),
        reasons=[request.reason],
        recommendations=["You may contact support to understand next steps."] if decision == "rejected" else ["Please complete KYC and disbursement formalities."],
    )

    return {"message": "Decision applied", "decision": decision}


@router.post("/cases/override")
async def override_decision(
    request: OverrideDecisionRequest,
    current_user: AuthUser = Depends(require_roles("underwriter", "risk_manager", "admin")),
):
    loan_id = request.loan_id
    if not ObjectId.is_valid(loan_id):
        raise HTTPException(status_code=400, detail="Invalid loan_id")

    case = loan_applications_collection.find_one({"_id": ObjectId(loan_id)})
    if not case:
        raise HTTPException(status_code=404, detail="Loan case not found")

    from_decision = request.from_decision.strip().lower()
    to_decision = request.to_decision.strip().lower()
    if from_decision == to_decision:
        raise HTTPException(status_code=400, detail="Override must change decision")

    if to_decision not in {"approved", "rejected"}:
        raise HTTPException(status_code=400, detail="to_decision must be approved/rejected")

    loan_applications_collection.update_one(
        {"_id": ObjectId(loan_id)},
        {
            "$set": {
                "status": to_decision,
                "final_decision": to_decision,
                "override": {
                    "from_decision": from_decision,
                    "to_decision": to_decision,
                    "reason": request.reason,
                    "actor": current_user["email"],
                    "actor_role": current_user["role"],
                    "at": datetime.utcnow(),
                },
                "updated_at": datetime.utcnow(),
            }
        },
    )

    loan_predictions_collection.update_many(
        {"email": case.get("email")},
        {
            "$set": {
                "override": {
                    "from_decision": from_decision,
                    "to_decision": to_decision,
                    "reason": request.reason,
                    "actor": current_user["email"],
                    "actor_role": current_user["role"],
                    "at": datetime.utcnow(),
                }
            }
        },
    )

    log_audit_event(
        action="loan.decision.overridden",
        actor_email=current_user["email"],
        actor_role=current_user["role"],
        entity_type="loan",
        entity_id=loan_id,
        metadata={
            "from_decision": from_decision,
            "to_decision": to_decision,
            "reason": request.reason,
        },
    )

    _send_workflow_decision_email(
        to_email=str(case.get("email", "")).strip().lower(),
        applicant_name=str(case.get("full_name", "Applicant")),
        decision=to_decision,
        requested_amount=float(case.get("loan_amount", 0) or 0),
        reasons=[f"Decision overridden: {from_decision} -> {to_decision}", request.reason],
        recommendations=["Please review updated decision details in your dashboard."],
    )

    return {"message": "Decision override applied", "decision": to_decision}


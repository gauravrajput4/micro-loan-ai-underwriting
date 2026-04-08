from fastapi import APIRouter, Depends

try:
    from ..database.mongodb import audit_logs_collection
    from ..services.security import AuthUser, require_roles
except (ModuleNotFoundError, ImportError):
    from database.mongodb import audit_logs_collection
    from services.security import AuthUser, require_roles


router = APIRouter()


@router.get("/events")
async def list_audit_events(
    limit: int = 100,
    current_user: AuthUser = Depends(require_roles("auditor", "admin", "risk_manager")),
):
    _ = current_user
    docs = list(audit_logs_collection.find().sort("created_at", -1).limit(min(limit, 500)))
    for d in docs:
        d["_id"] = str(d["_id"])
    return {"events": docs}


@router.get("/loan/{loan_id}")
async def loan_audit_events(
    loan_id: str,
    current_user: AuthUser = Depends(require_roles("auditor", "admin", "risk_manager", "underwriter")),
):
    _ = current_user
    docs = list(audit_logs_collection.find({"entity_type": "loan", "entity_id": loan_id}).sort("created_at", -1))
    for d in docs:
        d["_id"] = str(d["_id"])
    return {"events": docs}


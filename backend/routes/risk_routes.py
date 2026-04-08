from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

try:
    from ..services.security import AuthUser, require_roles
    from ..services.model_monitoring import compute_monitoring_snapshot
    from ..services.fairness_checks import run_fairness_check
    from ..services.model_registry import promote_version, rollback_to_version
    from ..jobs.retraining_pipeline import run_retraining_job
except (ModuleNotFoundError, ImportError):
    from services.security import AuthUser, require_roles
    from services.model_monitoring import compute_monitoring_snapshot
    from services.fairness_checks import run_fairness_check
    from services.model_registry import promote_version, rollback_to_version
    from jobs.retraining_pipeline import run_retraining_job


router = APIRouter()


class VersionRequest(BaseModel):
    version: str


@router.post("/monitoring/snapshot")
async def monitoring_snapshot(current_user: AuthUser = Depends(require_roles("admin", "risk_manager", "auditor"))):
    _ = current_user
    return compute_monitoring_snapshot()


@router.post("/fairness/report")
async def fairness_report(group_field: str = "employment_status", current_user: AuthUser = Depends(require_roles("admin", "risk_manager", "auditor"))):
    _ = current_user
    return run_fairness_check(group_field=group_field)


@router.post("/retrain")
async def retrain_model(current_user: AuthUser = Depends(require_roles("admin", "risk_manager"))):
    _ = current_user
    return run_retraining_job()


@router.post("/promote")
async def promote_model(payload: VersionRequest, current_user: AuthUser = Depends(require_roles("admin", "risk_manager"))):
    _ = current_user
    try:
        return promote_version(payload.version, model_type="champion")
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.post("/rollback")
async def rollback_model(payload: VersionRequest, current_user: AuthUser = Depends(require_roles("admin", "risk_manager"))):
    _ = current_user
    try:
        return rollback_to_version(payload.version, model_type="champion")
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


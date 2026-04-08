try:
    from ..services.model_monitoring import compute_monitoring_snapshot
    from ..services.fairness_checks import run_fairness_check
except (ModuleNotFoundError, ImportError):
    from services.model_monitoring import compute_monitoring_snapshot
    from services.fairness_checks import run_fairness_check


if __name__ == "__main__":
    snapshot = compute_monitoring_snapshot()
    report = run_fairness_check("employment_status")
    print({"monitoring": snapshot, "fairness": report})


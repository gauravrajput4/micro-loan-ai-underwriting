import os
import pickle
import shutil
from datetime import datetime

try:
    from ..database.mongodb import retraining_jobs_collection
    from ..ml.train_model import train_model
    from ..services.model_registry import ARTIFACTS_DIR, register_model_version
except (ModuleNotFoundError, ImportError):
    from database.mongodb import retraining_jobs_collection
    from ml.train_model import train_model
    from services.model_registry import ARTIFACTS_DIR, register_model_version


def run_retraining_job() -> dict:
    job = {
        "status": "running",
        "started_at": datetime.utcnow(),
    }
    result = retraining_jobs_collection.insert_one(job)
    job_id = result.inserted_id

    try:
        model, scaler, threshold = train_model()
        version = datetime.utcnow().strftime("v%Y%m%d_%H%M%S")
        out_dir = os.path.join(ARTIFACTS_DIR, version)
        os.makedirs(out_dir, exist_ok=True)

        # Copy latest artifacts into versioned location.
        ml_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "ml")
        for name in ["loan_model.pkl", "scaler.pkl", "model_config.pkl"]:
            shutil.copy2(os.path.join(ml_dir, name), os.path.join(out_dir, name))

        metrics = {"optimal_threshold": float(threshold)}
        register_model_version(
            version=version,
            model_type="champion",
            artifact_dir=out_dir,
            metrics=metrics,
            active=True,
        )

        retraining_jobs_collection.update_one(
            {"_id": job_id},
            {
                "$set": {
                    "status": "completed",
                    "version": version,
                    "completed_at": datetime.utcnow(),
                    "metrics": metrics,
                }
            },
        )
        return {"status": "completed", "version": version, "metrics": metrics}
    except Exception as exc:
        retraining_jobs_collection.update_one(
            {"_id": job_id},
            {
                "$set": {
                    "status": "failed",
                    "error": str(exc),
                    "completed_at": datetime.utcnow(),
                }
            },
        )
        raise


if __name__ == "__main__":
    print(run_retraining_job())


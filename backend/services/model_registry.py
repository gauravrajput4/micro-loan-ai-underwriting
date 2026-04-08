import os
import pickle
from datetime import datetime
from typing import Dict, Optional

try:
    from ..database.mongodb import model_registry_collection
except (ModuleNotFoundError, ImportError):
    from database.mongodb import model_registry_collection


ML_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "ml")
ARTIFACTS_DIR = os.path.join(ML_DIR, "artifacts")


def _load_pickle(path: str):
    with open(path, "rb") as f:
        return pickle.load(f)


def get_active_model_info(model_type: str = "champion") -> Optional[Dict]:
    return model_registry_collection.find_one(
        {"model_type": model_type, "active": True},
        sort=[("created_at", -1)],
    )


def register_model_version(*, version: str, model_type: str, artifact_dir: str, metrics: Dict, active: bool = False) -> Dict:
    if active:
        model_registry_collection.update_many({"model_type": model_type, "active": True}, {"$set": {"active": False}})

    doc = {
        "version": version,
        "model_type": model_type,
        "artifact_dir": artifact_dir,
        "metrics": metrics,
        "active": active,
        "created_at": datetime.utcnow(),
    }
    model_registry_collection.insert_one(doc)
    return doc


def load_model_bundle(model_type: str = "champion") -> Dict:
    info = get_active_model_info(model_type)

    if info and os.path.isdir(info["artifact_dir"]):
        model_path = os.path.join(info["artifact_dir"], "loan_model.pkl")
        scaler_path = os.path.join(info["artifact_dir"], "scaler.pkl")
        config_path = os.path.join(info["artifact_dir"], "model_config.pkl")
        if os.path.exists(model_path) and os.path.exists(scaler_path) and os.path.exists(config_path):
            return {
                "model": _load_pickle(model_path),
                "scaler": _load_pickle(scaler_path),
                "config": _load_pickle(config_path),
                "version": info.get("version", "unknown"),
            }

    # Fallback to root artifacts.
    model_path = os.path.join(ML_DIR, "loan_model.pkl")
    scaler_path = os.path.join(ML_DIR, "scaler.pkl")
    config_path = os.path.join(ML_DIR, "model_config.pkl")
    return {
        "model": _load_pickle(model_path),
        "scaler": _load_pickle(scaler_path),
        "config": _load_pickle(config_path),
        "version": "fallback-local",
    }


def promote_version(version: str, model_type: str = "champion") -> Dict:
    candidate = model_registry_collection.find_one({"version": version, "model_type": model_type})
    if not candidate:
        raise ValueError(f"Version not found: {version}")

    model_registry_collection.update_many({"model_type": model_type, "active": True}, {"$set": {"active": False}})
    model_registry_collection.update_one({"_id": candidate["_id"]}, {"$set": {"active": True, "promoted_at": datetime.utcnow()}})
    return {"version": version, "model_type": model_type, "active": True}


def rollback_to_version(version: str, model_type: str = "champion") -> Dict:
    return promote_version(version, model_type=model_type)


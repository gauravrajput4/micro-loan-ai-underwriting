from datetime import datetime
from typing import Dict, Optional

import pandas as pd

try:
    from ..database.mongodb import shadow_predictions_collection
    from .model_registry import load_model_bundle
except (ModuleNotFoundError, ImportError):
    from database.mongodb import shadow_predictions_collection
    from services.model_registry import load_model_bundle


def evaluate_challenger_shadow(
    *,
    email: str,
    features_df: pd.DataFrame,
    champion_probability: float,
    champion_decision: int,
    request_id: Optional[str] = None,
) -> Optional[Dict]:
    try:
        challenger = load_model_bundle("challenger")
    except Exception:
        return None

    model = challenger["model"]
    scaler = challenger["scaler"]
    config = challenger["config"]
    feature_names = config.get("feature_names") or list(features_df.columns)

    input_df = features_df.reindex(columns=feature_names)
    scaled = scaler.transform(input_df)
    proba = float(model.predict_proba(scaled)[0][1])
    threshold = float(config.get("optimal_threshold", 0.5))
    decision = 1 if proba >= threshold else 0

    doc = {
        "email": (email or "").strip().lower(),
        "request_id": request_id,
        "champion_probability": float(champion_probability),
        "champion_decision": int(champion_decision),
        "challenger_probability": proba,
        "challenger_decision": int(decision),
        "probability_delta": round(proba - float(champion_probability), 6),
        "decision_changed": bool(int(decision) != int(champion_decision)),
        "challenger_version": challenger.get("version", "unknown"),
        "created_at": datetime.utcnow(),
    }
    shadow_predictions_collection.insert_one(doc)
    return doc


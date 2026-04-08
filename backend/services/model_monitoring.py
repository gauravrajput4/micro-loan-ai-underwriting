from datetime import datetime
from typing import Dict, Iterable, List

import numpy as np

try:
    from ..database.mongodb import monitoring_snapshots_collection, loan_predictions_collection
except (ModuleNotFoundError, ImportError):
    from database.mongodb import monitoring_snapshots_collection, loan_predictions_collection


def _psi(expected: np.ndarray, actual: np.ndarray, bins: int = 10) -> float:
    if len(expected) == 0 or len(actual) == 0:
        return 0.0

    edges = np.quantile(expected, np.linspace(0, 1, bins + 1))
    edges = np.unique(edges)
    if len(edges) < 3:
        return 0.0

    expected_counts, _ = np.histogram(expected, bins=edges)
    actual_counts, _ = np.histogram(actual, bins=edges)

    expected_pct = np.clip(expected_counts / max(len(expected), 1), 1e-6, None)
    actual_pct = np.clip(actual_counts / max(len(actual), 1), 1e-6, None)
    return float(np.sum((actual_pct - expected_pct) * np.log(actual_pct / expected_pct)))


def _approval_rate(records: List[Dict]) -> float:
    if not records:
        return 0.0
    approved = sum(1 for r in records if int(r.get("prediction", 0)) == 1)
    return approved / len(records)


def compute_monitoring_snapshot() -> Dict:
    records = list(loan_predictions_collection.find().sort("created_at", 1))
    if not records:
        snapshot = {
            "created_at": datetime.utcnow(),
            "record_count": 0,
            "psi_probability": 0.0,
            "approval_rate_total": 0.0,
            "approval_rate_recent": 0.0,
            "approval_rate_shift": 0.0,
            "segment_performance": {},
        }
        monitoring_snapshots_collection.insert_one(snapshot)
        return snapshot

    split_idx = max(1, int(len(records) * 0.7))
    expected = records[:split_idx]
    actual = records[split_idx:]

    expected_prob = np.array([float(r.get("probability", 0.0)) for r in expected])
    actual_prob = np.array([float(r.get("probability", 0.0)) for r in actual])

    approval_total = _approval_rate(records)
    approval_recent = _approval_rate(actual)

    segments: Dict[str, Dict[str, float]] = {}
    for key in ["credit_rating"]:
        groups: Dict[str, List[Dict]] = {}
        for r in records:
            label = str(r.get(key, "UNKNOWN"))
            groups.setdefault(label, []).append(r)
        segments[key] = {
            k: round(_approval_rate(v), 4)
            for k, v in groups.items()
        }

    snapshot = {
        "created_at": datetime.utcnow(),
        "record_count": len(records),
        "psi_probability": round(_psi(expected_prob, actual_prob), 6),
        "approval_rate_total": round(approval_total, 6),
        "approval_rate_recent": round(approval_recent, 6),
        "approval_rate_shift": round(approval_recent - approval_total, 6),
        "segment_performance": segments,
    }
    monitoring_snapshots_collection.insert_one(snapshot)
    return snapshot


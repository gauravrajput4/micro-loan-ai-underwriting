import hashlib
import json
from datetime import datetime
from typing import Any, Dict, Optional

try:
    from ..database.mongodb import audit_logs_collection
except (ModuleNotFoundError, ImportError):
    from database.mongodb import audit_logs_collection


def _normalize_metadata(metadata: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    if not metadata:
        return {}
    return metadata


def log_audit_event(
    *,
    action: str,
    actor_email: str,
    actor_role: str,
    entity_type: str,
    entity_id: str,
    metadata: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    previous = audit_logs_collection.find_one(sort=[("created_at", -1)])
    prev_hash = previous.get("event_hash") if previous else "GENESIS"

    event = {
        "action": action,
        "actor_email": (actor_email or "").strip().lower(),
        "actor_role": actor_role,
        "entity_type": entity_type,
        "entity_id": str(entity_id),
        "metadata": _normalize_metadata(metadata),
        "created_at": datetime.utcnow(),
        "prev_hash": prev_hash,
    }

    canonical = json.dumps(
        {
            "action": event["action"],
            "actor_email": event["actor_email"],
            "actor_role": event["actor_role"],
            "entity_type": event["entity_type"],
            "entity_id": event["entity_id"],
            "metadata": event["metadata"],
            "created_at": event["created_at"].isoformat(),
            "prev_hash": event["prev_hash"],
        },
        sort_keys=True,
        separators=(",", ":"),
    )

    event_hash = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
    event["event_hash"] = event_hash

    audit_logs_collection.insert_one(event)
    return event


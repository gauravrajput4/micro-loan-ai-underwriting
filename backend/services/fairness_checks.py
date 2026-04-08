from datetime import datetime
from typing import Dict, List

try:
    from ..database.mongodb import fairness_reports_collection, loan_predictions_collection
except (ModuleNotFoundError, ImportError):
    from database.mongodb import fairness_reports_collection, loan_predictions_collection


def _confusion_counts(rows: List[Dict]) -> Dict[str, int]:
    tp = fp = tn = fn = 0
    for row in rows:
        y_true = row.get("actual_outcome")
        y_pred = row.get("prediction")
        if y_true is None:
            continue
        y_true = int(y_true)
        y_pred = int(y_pred)
        if y_true == 1 and y_pred == 1:
            tp += 1
        elif y_true == 0 and y_pred == 1:
            fp += 1
        elif y_true == 0 and y_pred == 0:
            tn += 1
        elif y_true == 1 and y_pred == 0:
            fn += 1
    return {"tp": tp, "fp": fp, "tn": tn, "fn": fn}


def run_fairness_check(group_field: str = "employment_status") -> Dict:
    rows = list(loan_predictions_collection.find())
    grouped: Dict[str, List[Dict]] = {}

    for row in rows:
        label = str(row.get(group_field, "unknown"))
        grouped.setdefault(label, []).append(row)

    metrics = {}
    for label, subset in grouped.items():
        approved = sum(1 for r in subset if int(r.get("prediction", 0)) == 1)
        total = len(subset)
        approval_rate = approved / total if total else 0.0

        cm = _confusion_counts(subset)
        denom_fpr = cm["fp"] + cm["tn"]
        denom_fnr = cm["fn"] + cm["tp"]
        fpr = cm["fp"] / denom_fpr if denom_fpr else 0.0
        fnr = cm["fn"] / denom_fnr if denom_fnr else 0.0

        metrics[label] = {
            "count": total,
            "approval_rate": round(approval_rate, 6),
            "false_positive_rate": round(fpr, 6),
            "false_negative_rate": round(fnr, 6),
        }

    rates = [v["approval_rate"] for v in metrics.values()]
    parity_gap = (max(rates) - min(rates)) if rates else 0.0

    report = {
        "created_at": datetime.utcnow(),
        "group_field": group_field,
        "metrics": metrics,
        "approval_parity_gap": round(parity_gap, 6),
    }
    fairness_reports_collection.insert_one(report)
    return report


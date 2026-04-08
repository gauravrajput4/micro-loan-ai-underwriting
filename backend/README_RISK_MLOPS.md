# Risk/ML Governance MVP

This module set adds industry-oriented risk controls:

- Champion-challenger shadow scoring
- Monitoring snapshots (PSI, approval-rate shifts, segment rates)
- Explainability reject codes (policy reason codes)
- Policy engine (score + business rules)
- Fairness checks (approval parity/FPR/FNR by group)
- Retraining job with versioned artifacts and registry promotion/rollback

## New APIs

- `POST /api/risk/monitoring/snapshot`
- `POST /api/risk/fairness/report?group_field=employment_status`
- `POST /api/risk/retrain`
- `POST /api/risk/promote` `{ "version": "vYYYYMMDD_HHMMSS" }`
- `POST /api/risk/rollback` `{ "version": "..." }`

## New Services

- `backend/services/policy_engine.py`
- `backend/services/model_registry.py`
- `backend/services/shadow_evaluator.py`
- `backend/services/model_monitoring.py`
- `backend/services/fairness_checks.py`

## Jobs

- `backend/jobs/retraining_pipeline.py`
- `backend/jobs/run_monitoring_snapshot.py`

## Quick Try

```bash
cd '/Users/apple/WorkSpace/Micro Loan'
source .venv/bin/activate
python -m unittest backend.tests.test_policy_engine backend.tests.test_monitoring_metrics backend.tests.test_fairness_checks
python backend/ml/train_model.py
python backend/main.py
```

## Notes

- Shadow mode expects a challenger entry in `model_registry` with active `model_type='challenger'`.
- Policy codes are returned under `policy_checks.reason_codes` and copied to explanation as `adverse_action_codes` on rejections.


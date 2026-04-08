# Enterprise MVP Features Added

This project now includes a working MVP for:

- KYC upload and verification (`PAN`, `Aadhaar`, `Passport`, selfie + mock liveness)
- Loan lifecycle workflow (`draft/submitted/under_review/approved/rejected/disbursed/closed/defaulted`)
- RBAC (`applicant`, `underwriter`, `risk_manager`, `admin`, `auditor`, plus existing `student`/`unemployed`)
- Tamper-evident audit logs (`prev_hash` + `event_hash` chain)
- Hardened auth (refresh token, OTP, MFA toggle, password reset)
- Decision override with mandatory reason
- Production-style HTML decision emails for approved/rejected outcomes

## New Backend APIs

- Auth: `/api/auth/refresh`, `/api/auth/logout`, `/api/auth/otp/request`, `/api/auth/otp/verify`, `/api/auth/password-reset/request`, `/api/auth/password-reset/confirm`, `/api/auth/mfa/config`
- KYC: `/api/kyc/documents`, `/api/kyc/selfie`, `/api/kyc/liveness/verify`, `/api/kyc/status/{loan_id}`, `/api/kyc/review/{loan_id}`
- Workflow: `/api/workflow/cases/my`, `/api/workflow/cases/{loan_id}/transition`, `/api/workflow/cases/{loan_id}/decision`, `/api/workflow/cases/override`
- Audit: `/api/audit/events`, `/api/audit/loan/{loan_id}`

## New Frontend Pages

- `KycVerification.tsx`
- `LoanQueue.tsx`
- `AuditViewer.tsx`
- `SecuritySettings.tsx`

## Quick Smoke Test

Run from workspace root:

```bash
source .venv/bin/activate
python -m unittest backend.tests.test_kyc_engine
python -m backend.main
```

Frontend:

```bash
cd frontend
npm install
npm run dev
```

## Notes

- OCR/liveness are mocked in `backend/services/kyc_engine.py` for MVP demonstration.
- In production, replace mock KYC checks with provider integrations and secure secret management.
- For OTP and password reset, debug values are returned when `DEBUG_SHOW_OTP=true`.
- If you hit import path errors, run commands from workspace root (`Micro Loan/`) using `python -m ...` package mode.

## SMTP Setup

1. Create `backend/.env` from `backend/.env.example`.
2. Fill SMTP values for your provider.
3. Keep `DEBUG_SHOW_OTP=false` in non-dev environments.

Example:

```dotenv
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your_email@gmail.com
SMTP_PASSWORD=your_app_password
SMTP_FROM=your_email@gmail.com
SMTP_USE_TLS=true
DEBUG_SHOW_OTP=false
```

Quick verification:

1. `POST /api/auth/signup/request-otp`
2. Check mailbox (and spam folder).
3. `POST /api/auth/signup/verify-otp`
4. `POST /api/auth/register`


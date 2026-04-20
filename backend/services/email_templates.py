from html import escape
from typing import Iterable

COMPANY_NAME = "LoanMint"
COMPANY_TAGLINE = "AI-powered fair financing for education and essential needs"


def _base_email_shell(*, title: str, subtitle: str, body_html: str) -> str:
    return f"""
<!doctype html>
<html>
  <body style="margin:0;padding:0;background:#f3f4f6;font-family:Arial,sans-serif;color:#111827;">
    <table role="presentation" width="100%" cellspacing="0" cellpadding="0" style="background:#f3f4f6;padding:24px 0;">
      <tr>
        <td align="center">
          <table role="presentation" width="640" cellspacing="0" cellpadding="0" style="width:640px;max-width:92%;background:#ffffff;border-radius:14px;overflow:hidden;border:1px solid #e5e7eb;">
            <tr>
              <td style="padding:18px 24px;background:#111827;color:#ffffff;">
                <div style="font-size:22px;font-weight:700;letter-spacing:0.2px;">{COMPANY_NAME}</div>
                <div style="font-size:13px;opacity:0.9;margin-top:2px;">{COMPANY_TAGLINE}</div>
              </td>
            </tr>
            <tr>
              <td style="padding:24px;">
                <h2 style="margin:0 0 6px;font-size:20px;color:#111827;">{escape(title)}</h2>
                <p style="margin:0 0 14px;font-size:14px;color:#4b5563;">{escape(subtitle)}</p>
                {body_html}
                <p style="margin:20px 0 0;font-size:13px;color:#6b7280;">If you did not request this action, you can safely ignore this email.</p>
              </td>
            </tr>
          </table>
        </td>
      </tr>
    </table>
  </body>
</html>
""".strip()


def _list_html(items: Iterable[str]) -> str:
    safe_items = [f"<li>{escape(str(item))}</li>" for item in items if str(item).strip()]
    if not safe_items:
        return ""
    return "<ul style='margin:8px 0 0 20px; padding:0;'>" + "".join(safe_items) + "</ul>"


def build_loan_decision_email(
    *,
    decision: str,
    applicant_name: str,
    requested_amount: float,
    reasons: list[str] | None = None,
    recommendations: list[str] | None = None,
) -> dict:
    decision_lower = (decision or "").strip().lower()
    is_approved = decision_lower == "approved"

    applicant = escape(applicant_name or "Applicant")
    amount = f"₹{float(requested_amount or 0):,.2f}"

    subject = (
        f"{COMPANY_NAME} Loan Approval Confirmation"
        if is_approved
        else f"{COMPANY_NAME} Loan Application Update"
    )

    status_chip = (
        "<span style='display:inline-block;padding:6px 12px;border-radius:999px;background:#dcfce7;color:#166534;font-weight:600;'>Approved</span>"
        if is_approved
        else "<span style='display:inline-block;padding:6px 12px;border-radius:999px;background:#fee2e2;color:#991b1b;font-weight:600;'>Rejected</span>"
    )

    intro = (
        "Congratulations. Your loan application has been approved based on our credit and affordability assessment."
        if is_approved
        else "We are unable to approve your loan application at this time based on our risk and policy assessment."
    )

    reason_block = ""
    if reasons:
        reason_block = (
            "<h3 style='margin:16px 0 6px;font-size:15px;color:#111827;'>Decision Factors</h3>"
            + _list_html(reasons)
        )

    recommendation_block = ""
    if recommendations:
        recommendation_block = (
            "<h3 style='margin:16px 0 6px;font-size:15px;color:#111827;'>What You Can Do Next</h3>"
            + _list_html(recommendations)
        )

    plain_text = (
        f"{COMPANY_NAME} - {COMPANY_TAGLINE}\n\n"
        f"Hello {applicant},\n\n"
        f"Loan Decision: {'APPROVED' if is_approved else 'REJECTED'}\n"
        f"Requested Amount: {amount}\n\n"
        f"{intro}\n\n"
    )

    if reasons:
        plain_text += "Decision Factors:\n" + "\n".join([f"- {r}" for r in reasons]) + "\n\n"
    if recommendations:
        plain_text += "What You Can Do Next:\n" + "\n".join([f"- {r}" for r in recommendations]) + "\n\n"

    plain_text += f"Thank you for choosing {COMPANY_NAME}."

    html = f"""
<!doctype html>
<html>
  <body style="margin:0;padding:0;background:#f3f4f6;font-family:Arial,sans-serif;color:#111827;">
    <table role="presentation" width="100%" cellspacing="0" cellpadding="0" style="background:#f3f4f6;padding:24px 0;">
      <tr>
        <td align="center">
          <table role="presentation" width="640" cellspacing="0" cellpadding="0" style="width:640px;max-width:92%;background:#ffffff;border-radius:14px;overflow:hidden;border:1px solid #e5e7eb;">
            <tr>
              <td style="padding:18px 24px;background:#111827;color:#ffffff;">
                <div style="font-size:22px;font-weight:700;letter-spacing:0.2px;">{COMPANY_NAME}</div>
                <div style="font-size:13px;opacity:0.9;margin-top:2px;">{COMPANY_TAGLINE}</div>
              </td>
            </tr>
            <tr>
              <td style="padding:24px;">
                <p style="margin:0 0 8px;font-size:16px;">Hello {applicant},</p>
                <div style="margin:0 0 12px;">{status_chip}</div>
                <p style="margin:0 0 8px;font-size:15px;color:#374151;">{intro}</p>
                <p style="margin:0 0 8px;font-size:15px;"><strong>Requested Amount:</strong> {amount}</p>
                {reason_block}
                {recommendation_block}
                <p style="margin:18px 0 0;font-size:14px;color:#4b5563;">Thank you for choosing <strong>{COMPANY_NAME}</strong>.</p>
              </td>
            </tr>
          </table>
        </td>
      </tr>
    </table>
  </body>
</html>
""".strip()

    return {"subject": subject, "text": plain_text, "html": html}


def build_otp_email(*, applicant_name: str, otp_code: str, purpose: str, expiry_minutes: int) -> dict:
    user = escape(applicant_name or "Customer")
    purpose_text = escape((purpose or "verification").replace("_", " ").title())
    code = escape(str(otp_code))

    subject = f"{COMPANY_NAME} Verification Code"
    text = (
        f"{COMPANY_NAME}\n\n"
        f"Hello {user},\n"
        f"Use this OTP for {purpose_text}: {code}\n"
        f"This code expires in {int(expiry_minutes)} minutes."
    )

    body = f"""
<p style="margin:0 0 12px;font-size:15px;color:#374151;">Hello {user}, use the OTP below to continue <strong>{purpose_text}</strong>.</p>
<div style="margin:8px 0 12px;padding:14px 16px;border:1px dashed #9ca3af;border-radius:10px;background:#f9fafb;display:inline-block;">
  <span style="font-size:28px;letter-spacing:6px;font-weight:700;color:#111827;">{code}</span>
</div>
<p style="margin:0;font-size:14px;color:#4b5563;">This code will expire in <strong>{int(expiry_minutes)} minutes</strong>.</p>
""".strip()

    html = _base_email_shell(
        title="One-Time Password (OTP)",
        subtitle=f"Secure verification from {COMPANY_NAME}",
        body_html=body,
    )
    return {"subject": subject, "text": text, "html": html}


def build_password_reset_email(*, applicant_name: str, reset_token: str, expiry_minutes: int) -> dict:
    user = escape(applicant_name or "Customer")
    token = escape(str(reset_token))
    subject = f"{COMPANY_NAME} Password Reset Instructions"

    text = (
        f"{COMPANY_NAME}\n\n"
        f"Hello {user},\n"
        f"Use this reset token to change your password:\n{token}\n"
        f"Token expires in {int(expiry_minutes)} minutes."
    )

    body = f"""
<p style="margin:0 0 12px;font-size:15px;color:#374151;">Hello {user}, we received a password reset request for your {COMPANY_NAME} account.</p>
<p style="margin:0 0 8px;font-size:14px;color:#374151;">Use the token below to reset your password:</p>
<div style="margin:8px 0 12px;padding:12px 14px;border:1px solid #d1d5db;border-radius:10px;background:#f9fafb;word-break:break-all;">
  <code style="font-size:13px;color:#111827;">{token}</code>
</div>
<p style="margin:0;font-size:14px;color:#4b5563;">This token expires in <strong>{int(expiry_minutes)} minutes</strong>.</p>
""".strip()

    html = _base_email_shell(
        title="Password Reset",
        subtitle=f"Secure account recovery for {COMPANY_NAME}",
        body_html=body,
    )
    return {"subject": subject, "text": text, "html": html}



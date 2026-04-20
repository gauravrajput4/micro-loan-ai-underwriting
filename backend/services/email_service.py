import os
import smtplib
from email.message import EmailMessage


def send_email(to_email: str, subject: str, body: str, html_body: str | None = None) -> bool:
    smtp_host = os.getenv("SMTP_HOST")
    smtp_port = int(os.getenv("SMTP_PORT", "587"))
    smtp_user = os.getenv("SMTP_USER")
    smtp_password = os.getenv("SMTP_PASSWORD")
    smtp_from = os.getenv("SMTP_FROM", smtp_user or "noreply@LoanMint.com")
    use_tls = os.getenv("SMTP_USE_TLS", "true").lower() == "true"

    if not smtp_host:
        # Dev fallback when SMTP is not configured.
        print(f"[EMAIL-DEV] To: {to_email} | Subject: {subject} | Body: {body}")
        return False

    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = smtp_from
    msg["To"] = to_email
    msg.set_content(body)
    if html_body:
        msg.add_alternative(html_body, subtype="html")

    try:
        with smtplib.SMTP(smtp_host, smtp_port, timeout=15) as server:
            if use_tls:
                server.starttls()
            if smtp_user and smtp_password:
                server.login(smtp_user, smtp_password)
            server.send_message(msg)
        return True
    except Exception as exc:
        print(f"[EMAIL-ERROR] Failed to deliver message to {to_email}: {exc}")
        return False


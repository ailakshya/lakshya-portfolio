"""
email_sender.py
Supports three email providers (pick any one):
  1. Outlook / Hotmail — just your regular email + password ✅ EASIEST
  2. SendGrid API — free 100/day, works with any account
  3. Gmail SMTP — personal Gmail with App Password only

Outlook setup: just enter your @outlook.com / @hotmail.com / @live.com email
and your normal password in the sidebar. Nothing else needed.
"""
import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders


def _attach_resume(msg: MIMEMultipart, resume_path: str):
    """Attach a PDF resume file to the email message."""
    if resume_path and os.path.exists(resume_path):
        with open(resume_path, "rb") as f:
            part = MIMEBase("application", "octet-stream")
            part.set_payload(f.read())
        encoders.encode_base64(part)
        filename = os.path.basename(resume_path)
        part.add_header("Content-Disposition", f"attachment; filename={filename}")
        msg.attach(part)
        return True
    return False


def send_via_sendgrid(
    api_key: str,
    sender_email: str,
    recipient_email: str,
    subject: str,
    body: str,
    resume_path: str = None,
    portfolio_url: str = "https://ailakshya.in"
) -> tuple:
    """Send via SendGrid HTTP API. Works with any Google/email account."""
    try:
        import urllib.request
        import json

        full_body = body
        if portfolio_url and portfolio_url not in body:
            full_body += f"\n\n🌐 Portfolio: {portfolio_url}"

        payload = {
            "personalizations": [{"to": [{"email": recipient_email}]}],
            "from": {"email": sender_email},
            "subject": subject,
            "content": [{"type": "text/plain", "value": full_body}]
        }

        # Add resume as attachment if present
        if resume_path and os.path.exists(resume_path):
            import base64
            with open(resume_path, "rb") as f:
                encoded = base64.b64encode(f.read()).decode()
            payload["attachments"] = [{
                "content": encoded,
                "type": "application/pdf",
                "filename": os.path.basename(resume_path),
                "disposition": "attachment"
            }]

        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            "https://api.sendgrid.com/v3/mail/send",
            data=data,
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            },
            method="POST"
        )
        with urllib.request.urlopen(req, timeout=10) as resp:
            if resp.status in (200, 202):
                resume_note = " (+ resume attached)" if resume_path and os.path.exists(resume_path) else ""
                return True, f"✅ Email sent to {recipient_email} via SendGrid{resume_note}"
            else:
                return False, f"❌ SendGrid returned status {resp.status}"
    except Exception as e:
        error_msg = str(e)
        if "400" in error_msg or "403" in error_msg:
            return False, "❌ SendGrid error: Check your API key and make sure your sender email is verified at sendgrid.com."
        return False, f"❌ SendGrid error: {error_msg}"


def send_via_gmail(
    sender_email: str,
    app_password: str,
    recipient_email: str,
    subject: str,
    body: str,
    resume_path: str = None,
    portfolio_url: str = "https://ailakshya.in"
) -> tuple:
    """Send via Gmail SMTP (requires App Password — personal Gmail only)."""
    try:
        msg = MIMEMultipart()
        msg["From"] = sender_email
        msg["To"] = recipient_email
        msg["Subject"] = subject

        full_body = body
        if portfolio_url and portfolio_url not in body:
            full_body += f"\n\n🌐 Portfolio: {portfolio_url}"
        msg.attach(MIMEText(full_body, "plain"))

        has_resume = _attach_resume(msg, resume_path)

        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(sender_email, app_password)
            server.sendmail(sender_email, recipient_email, msg.as_string())

        resume_note = " (+ resume attached)" if has_resume else ""
        return True, f"✅ Email sent to {recipient_email} via Gmail{resume_note}"
    except smtplib.SMTPAuthenticationError:
        return False, "❌ Gmail auth failed. App Passwords require a personal Gmail with 2FA. Try Outlook instead."
    except Exception as e:
        return False, f"❌ Gmail error: {str(e)}"


def send_via_outlook(
    sender_email: str,
    password: str,
    recipient_email: str,
    subject: str,
    body: str,
    resume_path: str = None,
    portfolio_url: str = "https://ailakshya.in"
) -> tuple:
    """Send via Outlook/Hotmail SMTP using regular username + password. No special setup needed."""
    try:
        msg = MIMEMultipart()
        msg["From"] = sender_email
        msg["To"] = recipient_email
        msg["Subject"] = subject

        full_body = body
        if portfolio_url and portfolio_url not in body:
            full_body += f"\n\n🌐 Portfolio: {portfolio_url}"
        msg.attach(MIMEText(full_body, "plain"))

        has_resume = _attach_resume(msg, resume_path)

        with smtplib.SMTP("smtp.office365.com", 587) as server:
            server.starttls()
            server.login(sender_email, password)
            server.sendmail(sender_email, recipient_email, msg.as_string())

        resume_note = " (+ resume attached)" if has_resume else ""
        return True, f"✅ Email sent to {recipient_email} via Outlook{resume_note}"
    except smtplib.SMTPAuthenticationError:
        return False, "❌ Outlook auth failed. Check your email and password. Make sure it's an @outlook.com / @hotmail.com account."
    except Exception as e:
        return False, f"❌ Outlook error: {str(e)}"


def send_cold_email(
    sender_email: str,
    recipient_email: str,
    subject: str,
    body: str,
    resume_path: str = None,
    portfolio_url: str = "https://ailakshya.in",
    sendgrid_api_key: str = "",
    gmail_app_password: str = "",
    outlook_password: str = ""
) -> tuple:
    """
    Auto-selects provider in priority order:
    1. Outlook (regular password) if outlook_password provided
    2. SendGrid if API key provided
    3. Gmail SMTP if app password provided
    """
    if not recipient_email or "@" not in recipient_email:
        return False, "❌ Invalid recipient email address."

    if outlook_password and outlook_password.strip():
        return send_via_outlook(sender_email, outlook_password, recipient_email,
                                subject, body, resume_path, portfolio_url)
    elif sendgrid_api_key and sendgrid_api_key.strip():
        return send_via_sendgrid(sendgrid_api_key, sender_email, recipient_email,
                                  subject, body, resume_path, portfolio_url)
    elif gmail_app_password and gmail_app_password.strip():
        return send_via_gmail(sender_email, gmail_app_password, recipient_email,
                               subject, body, resume_path, portfolio_url)
    else:
        return False, "❌ Please add Outlook/Gmail credentials or a SendGrid API key in the sidebar."


def extract_subject_from_draft(email_body: str) -> str:
    """Extract the Subject line from a drafted cold email body."""
    for line in email_body.split("\n"):
        line = line.strip()
        if line.lower().startswith("subject:"):
            return line[8:].strip()
    return "Exciting Opportunity: AI/ML Engineer Application"



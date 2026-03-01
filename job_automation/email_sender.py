"""
email_sender.py
Gmail SMTP email sender for the AI Job Portal.
Supports attaching a resume PDF and including a portfolio website link.

Setup:
1. Enable 2FA on your Gmail account
2. Go to https://myaccount.google.com/apppasswords
3. Create an App Password named "Job Portal"
4. Use that 16-char password in the sidebar
"""
import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders


def send_cold_email(
    sender_email: str,
    sender_app_password: str,
    recipient_email: str,
    subject: str,
    body: str,
    resume_path: str = None,
    portfolio_url: str = "https://ailakshya.in"
) -> tuple:
    """
    Send a cold email via Gmail SMTP.
    Optionally attaches a resume PDF and appends portfolio link.
    Returns (success: bool, message: str)
    """
    if not sender_email or not sender_app_password:
        return False, "❌ Gmail address and App Password are required."
    if not recipient_email or "@" not in recipient_email:
        return False, "❌ Invalid recipient email address."

    try:
        msg = MIMEMultipart()
        msg["From"] = sender_email
        msg["To"] = recipient_email
        msg["Subject"] = subject

        # Append portfolio link to body
        full_body = body
        if portfolio_url and portfolio_url not in body:
            full_body += f"\n\n🌐 Portfolio: {portfolio_url}"

        msg.attach(MIMEText(full_body, "plain"))

        # Attach resume PDF if provided
        if resume_path and os.path.exists(resume_path):
            with open(resume_path, "rb") as f:
                part = MIMEBase("application", "octet-stream")
                part.set_payload(f.read())
            encoders.encode_base64(part)
            filename = os.path.basename(resume_path)
            part.add_header("Content-Disposition", f"attachment; filename={filename}")
            msg.attach(part)

        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(sender_email, sender_app_password)
            server.sendmail(sender_email, recipient_email, msg.as_string())

        resume_note = f" (+ resume attached)" if resume_path and os.path.exists(resume_path) else ""
        return True, f"✅ Email sent to {recipient_email}{resume_note}"

    except smtplib.SMTPAuthenticationError:
        return False, "❌ Gmail auth failed. Use an App Password, not your regular password."
    except smtplib.SMTPException as e:
        return False, f"❌ SMTP Error: {str(e)}"
    except Exception as e:
        return False, f"❌ Unexpected error: {str(e)}"


def extract_subject_from_draft(email_body: str) -> str:
    """Extract the Subject line from a drafted cold email body."""
    for line in email_body.split("\n"):
        line = line.strip()
        if line.lower().startswith("subject:"):
            return line[8:].strip()
    return "Exciting Opportunity: AI/ML Engineer Application"

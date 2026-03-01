"""
gmail_oauth.py
Sends emails through Gmail API using OAuth2.
Works with ANY Gmail account including Google Workspace.
No App Password needed — just log in with Google once.

One-time setup:
1. Go to https://console.cloud.google.com
2. Create a project → Enable "Gmail API"
3. OAuth consent screen → External → Add your email as test user
4. Credentials → Create OAuth 2.0 Client ID → Desktop App → Download JSON
5. Rename the downloaded file to "gmail_credentials.json" and place it in this folder
6. First send: a browser opens for Google login → token auto-saved → never needed again
"""
import os
import base64
import json
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

CREDENTIALS_FILE = "gmail_credentials.json"
TOKEN_FILE = "gmail_token.json"


def _get_gmail_service():
    """Authenticate and return a Gmail API service object."""
    try:
        from google.oauth2.credentials import Credentials
        from google_auth_oauthlib.flow import InstalledAppFlow
        from google.auth.transport.requests import Request
        from googleapiclient.discovery import build
    except ImportError:
        raise ImportError("Run: pip install google-auth-oauthlib google-api-python-client")

    SCOPES = ["https://www.googleapis.com/auth/gmail.send"]
    creds = None

    if os.path.exists(TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not os.path.exists(CREDENTIALS_FILE):
                raise FileNotFoundError(
                    f"Missing {CREDENTIALS_FILE}. Download from Google Cloud Console → "
                    "Credentials → OAuth 2.0 Client IDs → Download JSON"
                )
            flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, SCOPES)
            creds = flow.run_local_server(port=0)

        with open(TOKEN_FILE, "w") as token:
            token.write(creds.to_json())

    return build("gmail", "v1", credentials=creds)


def send_gmail_oauth(
    recipient_email: str,
    subject: str,
    body: str,
    resume_path: str = None,
    portfolio_url: str = "https://ailakshya.in"
) -> tuple:
    """
    Send one email via Gmail API (OAuth2). 
    Returns (success: bool, message: str)
    """
    try:
        service = _get_gmail_service()

        msg = MIMEMultipart()
        msg["To"] = recipient_email
        msg["Subject"] = subject

        full_body = body
        if portfolio_url and portfolio_url not in body:
            full_body += f"\n\n🌐 Portfolio: {portfolio_url}"
        msg.attach(MIMEText(full_body, "plain"))

        # Attach resume PDF
        has_resume = False
        if resume_path and os.path.exists(resume_path):
            with open(resume_path, "rb") as f:
                part = MIMEBase("application", "octet-stream")
                part.set_payload(f.read())
            encoders.encode_base64(part)
            filename = os.path.basename(resume_path)
            part.add_header("Content-Disposition", f"attachment; filename={filename}")
            msg.attach(part)
            has_resume = True

        raw = base64.urlsafe_b64encode(msg.as_bytes()).decode()
        service.users().messages().send(userId="me", body={"raw": raw}).execute()

        resume_note = " (+ resume attached)" if has_resume else ""
        return True, f"✅ Sent to {recipient_email} via Gmail{resume_note}"

    except FileNotFoundError as e:
        return False, f"❌ {str(e)}"
    except ImportError as e:
        return False, f"❌ {str(e)}"
    except Exception as e:
        err = str(e)
        if "invalid_grant" in err or "Token" in err:
            # Delete stale token and ask to re-auth
            if os.path.exists(TOKEN_FILE):
                os.remove(TOKEN_FILE)
            return False, "❌ Gmail token expired. Restart the app to re-authenticate."
        return False, f"❌ Gmail API error: {err}"


def is_gmail_oauth_ready() -> bool:
    """Check if gmail_credentials.json exists (setup has been done)."""
    return os.path.exists(CREDENTIALS_FILE)


def is_gmail_token_cached() -> bool:
    """Check if a valid Gmail token already exists (no login needed)."""
    return os.path.exists(TOKEN_FILE)

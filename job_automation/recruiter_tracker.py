"""
recruiter_tracker.py
A lightweight JSON-based CRM to track all recruiter outreach.
Remembers which companies/emails have been contacted and tracks status.
"""
import json
import os
from datetime import datetime

TRACKER_FILE = "recruiter_history.json"


def _load() -> list:
    if os.path.exists(TRACKER_FILE):
        try:
            with open(TRACKER_FILE, "r") as f:
                return json.load(f)
        except Exception:
            return []
    return []


def _save(records: list):
    with open(TRACKER_FILE, "w") as f:
        json.dump(records, f, indent=2)


def log_email_sent(job_title: str, company: str, recruiter_email: str,
                   email_subject: str, email_body: str, job_url: str = ""):
    """Record that an email was sent to this recruiter."""
    records = _load()
    record = {
        "id": f"{company.lower().replace(' ', '_')}_{datetime.now().strftime('%Y%m%d%H%M%S')}",
        "job_title": job_title,
        "company": company,
        "recruiter_email": recruiter_email,
        "email_subject": email_subject,
        "email_body": email_body,
        "job_url": job_url,
        "date_sent": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "status": "sent"  # sent | replied | offer | rejected | no_response
    }
    records.append(record)
    _save(records)
    return record["id"]


def get_all_records() -> list:
    return _load()


def get_record_for_company(company: str) -> list:
    """Return all past contacts for a given company."""
    records = _load()
    return [r for r in records if r["company"].lower() == company.lower()]


def get_record_for_email(email: str) -> list:
    """Return all past contacts to a given email."""
    records = _load()
    return [r for r in records if r["recruiter_email"].lower() == email.lower()]


def was_contacted(company: str, recruiter_email: str = "") -> dict | None:
    """
    Returns the most recent contact record if this company/email was
    already contacted, else None.
    """
    records = _load()
    matches = []
    for r in records:
        if r["company"].lower() == company.lower():
            matches.append(r)
        elif recruiter_email and r["recruiter_email"].lower() == recruiter_email.lower():
            matches.append(r)
    if not matches:
        return None
    # Return most recent
    return sorted(matches, key=lambda x: x["date_sent"], reverse=True)[0]


def update_status(record_id: str, new_status: str):
    """Update the status of a tracked outreach (e.g. 'replied', 'offer')."""
    records = _load()
    for r in records:
        if r["id"] == record_id:
            r["status"] = new_status
            break
    _save(records)

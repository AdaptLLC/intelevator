"""Email notification system using Resend API.

Ported from src/main.rs:218-265
"""
import resend
from datetime import datetime
from typing import Optional
import logging

from .config import settings

logger = logging.getLogger(__name__)


async def send_login_notification(client_ip: str) -> bool:
    """Send email notification when someone logs in with valid password.

    Args:
        client_ip: IP address of the client

    Returns:
        True if email sent successfully, False otherwise
    """
    # Check if Resend API key is configured
    if not settings.resend_api_key:
        logger.warning("Resend API key not configured, skipping email notification")
        return False

    # Set the API key
    resend.api_key = settings.resend_api_key

    # Format timestamp
    timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")

    # Compose email
    html_body = f"""
    <h2>Elevator System Access</h2>
    <p>Someone accessed the elevator system with a valid password.</p>
    <ul>
        <li><strong>IP Address:</strong> {client_ip}</li>
        <li><strong>Timestamp:</strong> {timestamp}</li>
    </ul>
    <p><em>This is an automated notification from the elevator system.</em></p>
    """

    text_body = f"""
    Someone accessed the elevator system with a valid password.

    IP Address: {client_ip}
    Timestamp: {timestamp}

    This is an automated notification from the elevator system.
    """

    try:
        # Send email using Resend SDK
        params: resend.Emails.SendParams = {
            "from": f"Elevator System <{settings.from_email}>",
            "to": [settings.admin_email],
            "subject": "Elevator System Access",
            "html": html_body,
            "text": text_body,
        }

        email = resend.Emails.send(params)
        logger.info(f"Login notification email sent successfully via Resend: {email['id']}")
        return True

    except Exception as e:
        logger.error(f"Failed to send email via Resend: {e}")
        return False

"""
AI Daily Digest — Email Sender
Sends the digest via QQ邮箱 SMTP (or any SMTP server).
"""

import logging
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import Header

from .config import email as email_cfg

logger = logging.getLogger(__name__)


def send_email(html_body: str, subject: str) -> bool:
    """
    Send email via SMTP (QQ邮箱 recommended).

    Returns True on success, False on failure.
    """
    if not email_cfg.smtp_user or not email_cfg.smtp_pass or not email_cfg.email_to:
        logger.error("Email config incomplete: SMTP_USER, SMTP_PASS, EMAIL_TO required")
        return False

    # Build multipart message
    msg = MIMEMultipart("alternative")
    msg["From"] = f"{email_cfg.email_from_name} <{email_cfg.smtp_user}>"
    msg["To"] = email_cfg.email_to
    msg["Subject"] = Header(subject, "utf-8")

    # Plain text fallback
    plain_text = _html_to_plain_text(html_body)
    msg.attach(MIMEText(plain_text, "plain", "utf-8"))
    msg.attach(MIMEText(html_body, "html", "utf-8"))

    # Send via SMTP
    try:
        if email_cfg.smtp_port == 465:
            # SSL
            with smtplib.SMTP_SSL(
                email_cfg.smtp_host, email_cfg.smtp_port, timeout=30
            ) as server:
                server.login(email_cfg.smtp_user, email_cfg.smtp_pass)
                server.send_message(msg)
        else:
            # STARTTLS (port 587)
            with smtplib.SMTP(
                email_cfg.smtp_host, email_cfg.smtp_port, timeout=30
            ) as server:
                server.starttls()
                server.login(email_cfg.smtp_user, email_cfg.smtp_pass)
                server.send_message(msg)

        logger.info(f"✓ Email sent to {email_cfg.email_to}")
        return True

    except smtplib.SMTPAuthenticationError:
        logger.error(
            "SMTP authentication failed. "
            "For QQ邮箱: use the 16-digit authorization code, NOT your password."
        )
        return False
    except smtplib.SMTPException as e:
        logger.error(f"SMTP error: {e}")
        return False
    except Exception as e:
        logger.error(f"Failed to send email: {e}")
        return False


def _html_to_plain_text(html: str) -> str:
    """Strip HTML tags for plain text fallback."""
    import re
    text = re.sub(r"<[^>]+>", "", html)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()

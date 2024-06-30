from email.message import EmailMessage

import aiosmtplib
from pydantic import EmailStr

from src.settings import EMAIL_PASSWORD, EMAIL_SENDER, FRONTEND_URL, lookup


async def send_mail(send_to: EmailStr, subject: str, context: str) -> None:
    """
    Send an email with the specified subject and content.

    Args:
        send_to (EmailStr): The recipient's email address.
        subject (str): The subject of the email.
        context (str): The content of the email.
    """
    em = EmailMessage()
    em["From"] = EMAIL_SENDER
    em["To"] = send_to
    em["Subject"] = subject

    em.add_alternative(context, subtype="html")

    await aiosmtplib.send(
        em,
        hostname="smtp.gmail.com",
        port=587,
        username=EMAIL_SENDER,
        password=EMAIL_PASSWORD,
    )


template = lookup.get_template("activate_account_email.html")


async def send_verification_email(mail: EmailStr, one_time_jwt: str) -> None:
    """
    Send a verification email with a one-time JWT token to activate user.

    Args:
        mail (EmailStr): The recipient's email address.
        one_time_jwt (str): The one-time JWT token for email verification.

    Returns:
        None
    """
    verification_endpoint = FRONTEND_URL + "/auth/verify-email?token="
    verification_url = verification_endpoint + one_time_jwt
    email_html = template.render(verification_url=verification_url)
    await send_mail(mail, "Verify Email", email_html)

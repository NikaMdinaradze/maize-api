from email.message import EmailMessage

import aiosmtplib
from pydantic import EmailStr

from src.settings import BACKEND_URL, EMAIL_PASSWORD, EMAIL_SENDER


async def send_mail(send_to: EmailStr, subject: str, context: str) -> None:
    em = EmailMessage()
    em["From"] = EMAIL_SENDER
    em["To"] = send_to
    em["Subject"] = subject

    em.add_alternative(context)

    await aiosmtplib.send(
        em,
        hostname="smtp.gmail.com",
        port=587,
        username=EMAIL_SENDER,
        password=EMAIL_PASSWORD,
    )


async def send_verification_email(mail: EmailStr, one_time_jwt: str) -> None:
    verification_endpoint = BACKEND_URL + "/auth/verify-email?token="
    verification_url = verification_endpoint + one_time_jwt
    await send_mail(mail, "Verify Email", verification_url)

from email.message import EmailMessage

import aiosmtplib
from pydantic import EmailStr

from src.settings import EMAIL_PASSWORD, EMAIL_SENDER


async def send_mail(send_to: EmailStr, context: str):
    em = EmailMessage()
    em["From"] = EMAIL_SENDER
    em["To"] = send_to
    em["Subject"] = "Verify Account"

    em.add_alternative(context)

    await aiosmtplib.send(
        em,
        hostname="smtp.gmail.com",
        port=587,
        username=EMAIL_SENDER,
        password=EMAIL_PASSWORD,
    )

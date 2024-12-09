import emails
from app.models.email import EmailError
from app.repositories.user import UserRepository
from app.repositories.email import EmailErrorRepository
from fastapi import HTTPException, status
from app.core.config import settings
from app.core.db import get_async_session
from .render_email_template import render_email_template
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def send_pair_email(giver_email: str, receiver_email: str):
    async with get_async_session() as db:
        user_repo = UserRepository(db)

        context = await user_repo.create_email_context(giver_email, receiver_email)

    subject = "Your Gift Pairing Details"
    body_html = render_email_template("secret_santa_email.html", context)

    try:
        await send_email(giver_email, receiver_email, subject, body_html)
    except Exception as e:
        async with get_async_session() as db:
            email_error = EmailError(
                giver_email=giver_email,
                receiver_email=receiver_email,
                error_message=str(e)
            )
            db.add(email_error)
            await db.commit()


async def send_email(giver_email: str, receiver_email: str, subject: str, body_html: str):
    message = emails.Message(
        subject=subject,
        html=body_html,
        mail_from=(settings.EMAILS_FROM_NAME, settings.SMTP_USER),
    )

    smtp_options = {"host": settings.SMTP_HOST, "port": settings.SMTP_PORT}
    if settings.SMTP_TLS:
        smtp_options["tls"] = True
    elif settings.SMTP_SSL:
        smtp_options["ssl"] = True
    if settings.SMTP_USER:
        smtp_options["user"] = settings.SMTP_USER
    if settings.SMTP_PASSWORD:
        smtp_options["password"] = settings.SMTP_PASSWORD

    try:
        response = message.send(to=receiver_email, smtp=smtp_options)
        logger.info(f"send email result: {response}")
    except Exception as e:
        logger.error(f"Failed to send email: {str(e)}")
        async with get_async_session() as db:
            email_error_repo = EmailErrorRepository(db)
            await email_error_repo.save_error(
                giver_email=giver_email,
                receiver_email=receiver_email,
                error_message=f"Failed to send email: {str(e)}"
            )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to send email: {str(e)}"
        )

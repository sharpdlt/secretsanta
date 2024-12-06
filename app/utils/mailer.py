import json
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.db import connect_to_rabbitmq, get_async_session
from app.models.email import EmailError
from app.repositories.user import UserRepository
from .render_email_template import render_email_template


async def send_pair_email(giver_email: str, receiver_email: str):
    async with get_async_session() as db:
        user_repo = UserRepository(db)

        context = await user_repo.create_email_context(giver_email, receiver_email)

    subject = "Your Gift Pairing Details"

    body_html = render_email_template("secret_santa_email.html", context)

    message = json.dumps({
        "giver_email": giver_email,
        "receiver_email": receiver_email,
        "subject": subject,
        "body_html": body_html
    })

    connection, channel = connect_to_rabbitmq()
    channel.queue_declare(queue='email_queue')
    channel.basic_publish(exchange='', routing_key='email_queue', body=message)

    connection.close()


async def log_email_error(db: AsyncSession, giver_email: str, receiver_email: str, error_message: str):
    email_error = EmailError(
        giver_email=giver_email,
        receiver_email=receiver_email,
        error_message=error_message
    )
    db.add(email_error)
    await db.commit()

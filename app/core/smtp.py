import asyncio
import json
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from app.core.config import settings
from app.repositories.email import EmailErrorRepository
from app.core.db import get_async_session, connect_to_rabbitmq


async def send_email(giver_email: str, receiver_email: str, subject: str, body_html: str):
    message = MIMEMultipart()
    message["From"] = settings.SMTP_USERNAME
    message["To"] = giver_email
    message["Subject"] = subject
    message.attach(MIMEText(body_html, "html"))

    try:
        with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
            server.starttls()
            server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
            server.sendmail(settings.SMTP_USERNAME, giver_email, message.as_string())
    except Exception as e:
        async with get_async_session() as db:
            email_error_repo = EmailErrorRepository(db)
            await email_error_repo.save_error(giver_email, receiver_email, str(e))


async def process_email_queue():
    def callback(channel, method, body):
        message = json.loads(body)
        asyncio.run(send_email(
            giver_email=message["giver_email"],
            receiver_email=message["receiver_email"],
            subject=message["subject"],
            body_html=message["body_html"],
        ))
        channel.basic_ack(delivery_tag=method.delivery_tag)

    connection, channel = connect_to_rabbitmq()
    channel.queue_declare(queue="email_queue")
    channel.basic_consume(queue="email_queue", on_message_callback=callback)

    try:
        channel.start_consuming()
    except KeyboardInterrupt:
        channel.stop_consuming()
        connection.close()

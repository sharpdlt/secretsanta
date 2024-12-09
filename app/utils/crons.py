from fastapi import APIRouter, BackgroundTasks
from .mailer import send_pair_email

router = APIRouter()


@router.post("/send-email")
async def send_email_endpoint(
        giver_email: str, receiver_email: str, background_tasks: BackgroundTasks
):
    background_tasks.add_task(send_pair_email, giver_email, receiver_email)
    return {"message": "Email будет отправлен в фоновом режиме."}

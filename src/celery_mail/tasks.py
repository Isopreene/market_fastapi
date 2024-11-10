from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
from .celery_config import celery_app
from src.app.routes.activate_and_reset import mail_cache
from config import settings
from asgiref.sync import async_to_sync


conf = ConnectionConfig(
    MAIL_USERNAME=settings.MAIL_USERNAME,
    MAIL_FROM=settings.MAIL_FROM,
    MAIL_PASSWORD=settings.MAIL_PASSWORD,
    MAIL_PORT=settings.MAIL_PORT,
    MAIL_SERVER=settings.MAIL_SERVER,
    MAIL_STARTTLS=True,
    MAIL_SSL_TLS=False,
)


@celery_app.task(name="send_email_user_activation_w")
def send_email_user_activation(email: str):
    result = async_to_sync(async_send_email)(email,
                                             route="auth/activate")
    return result

@celery_app.task(name="send_email_reset_password_w")
def send_email_reset_password(email: str):
    result = async_to_sync(async_send_email)(email,
                                             route="auth/reset_password")
    return result


async def async_send_email(email: str, route: str):
    """отправляем ссылку для подтверждения/восстановления аккаунта"""
    url = await mail_cache.generate(email, route)
    template = f"""
    <html>
        <body>
            <p>
                Ваша ссылка: {url}
            </p>
        </body>
    </html>
    """
    message = MessageSchema(
        subject="Fastapi-Mail module",
        recipients=[email,],
        body=template,
        subtype="html")

    fm = FastMail(conf)
    res = await fm.send_message(message)
    return res

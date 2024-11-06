from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
from .celery_config import celery_app
from src.app.routes.mail import mail_cache
from config import settings

conf = ConnectionConfig(
    MAIL_USERNAME=settings.MAIL_USERNAME,
    MAIL_FROM=settings.MAIL_FROM,
    MAIL_PASSWORD=settings.MAIL_PASSWORD,
    MAIL_PORT=settings.MAIL_PORT,
    MAIL_SERVER=settings.MAIL_SERVER,
    MAIL_STARTTLS=True,
    MAIL_SSL_TLS=False,
)


@celery_app.task
async def send_email(email: str, route: str):
    """отправляем ссылку для подтверждения/восстановления аккаунта"""
    url = mail_cache.generate_link(email, route)
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

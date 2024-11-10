import os
import binascii
from ..redis.crud_redis import get_value, set_value, delete_value
from config import settings

class MailCache:

    async def generate(self, email: str, route: str) -> str:
        """создать ссылку для активации"""
        secret_key = binascii.hexlify(os.urandom(10)).decode('utf-8')
        url = (f"http://{settings.BACKEND_HOST}:{settings.BACKEND_PORT}"
               f"/{route}?email={email}&secret_key={secret_key}")
        await set_value(email, secret_key)
        return url

    async def activate(self, email:str,
                 secret_key: str) -> (str | bool):
        """активировать и вернуть статус активации"""
        cache_secret_key = await get_value(email)
        if cache_secret_key == secret_key:
            await delete_value(email)
            return email
        else:
            return False

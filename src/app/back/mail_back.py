import os
import binascii
from config import settings


class Link:
    def __init__(self, email: str = None, secret_key: str = None):
        self.email = email
        self.secret_key = secret_key
        self.activated = False


class MailCache:
    def __init__(self):
        """Кэш для писем. В следующем проекте поменять на Redis"""
        self.links: list[Link] = []

    def pop_link(self, secret_key: str) -> Link | None:
        for link in self.links:
            if link.secret_key == secret_key:
                self.links.remove(link)
                return link
        return

    def generate_link(self, email: str, route: str) -> str:
        """создать ссылку для активации"""
        secret_key = binascii.hexlify(os.urandom(10)).decode('utf-8')
        self.links.append(Link(email, secret_key))
        url = (f"http://{settings.BACKEND_HOST}:{settings.BACKEND_PORT}"
               f"/{route}?secret_key"
               f"={secret_key}")
        return url

    def activate_link(self, secret_key) -> Link | bool:
        """активировать и вернуть статус активации"""
        link = self.pop_link(secret_key)
        if link.secret_key == secret_key and not link.activated:
            return link
        else:
            return False

import os
import binascii


class MailCache:
    def __init__(self):
        """Кэш для писем. В следующем проекте поменять на Redis"""
        self.links: list[dict] = []

    def generate_link(self):
        """создать ссылку для активации"""
        secret_key = binascii.hexlify(os.urandom(10)).decode('utf-8')
        self.links.append({"secret_key": secret_key, "activated": False})
        url = f"http://localhost:8000/activate_link?secret_key={secret_key}"
        return url

    def activate_link(self, secret_key):
        """активировать и вернуть статус активации"""
        try:
            key = self.links.pop(self.links.index({"secret_key": secret_key,
                                                   "activated": False}))
            if key["secret_key"] == secret_key and not key["activated"]:
                return True
            else:
                return False
        except [IndexError, ValueError]:
            return False
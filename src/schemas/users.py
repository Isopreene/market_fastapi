from pydantic import BaseModel, EmailStr
from pydantic_extra_types.phone_numbers import PhoneNumber


class UserReg(BaseModel):
    """Модель pydantic для описания пользователя для регистрации"""
    name: str
    email: EmailStr
    phone: PhoneNumber
    password: str
    class Config:
        json_schema_extra = {
            "example": {
                "name": "Иванов Иван Иванович",
                "email": "ivanovii@yandex.ru",
                "phone": "+79999999999",
                "password": "strongpassword"
            }
        }

class UserLogin(BaseModel):
    """Модель pydantic для описания пользователя для логина"""
    email: str
    password: str
    class Config:
        json_schema_extra = {
            "example": {
                "email": "ivanovii@yandex.ru",
                "password": "strongpassword"
            }
        }

class UserRecover(BaseModel):
    """Модель pydantic для описания пользователя для восстановления пароля"""
    email: str
    class Config:
        json_schema_extra = {
            "example": {
                "email": "ivanovii@yandex.ru"
            }
        }
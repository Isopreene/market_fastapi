import jwt
from datetime import datetime, timedelta
import os
import binascii
from passlib.context import CryptContext
from config import settings
from fastapi import Request

SECRET_KEY = settings.get('SECRET_KEY', binascii.hexlify(os.urandom(24)))
ALGORITHM = settings.get('ALGORITHM', 'HS256')
ACCESS_TOKEN_EXPIRE_MINUTES = settings.get('ACCESS_TOKEN_EXPIRE_MINUTES', 30)
pwd_context = CryptContext(schemes=["sha256_crypt"])


def get_password_hash(password):
    return pwd_context.hash(password)


def verify_password_hash(password, hashed_password):
    return pwd_context.verify(password, hashed_password)


def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.now() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY,
                             algorithm=ALGORITHM)
    return encoded_jwt


def get_params_from_decrypt_token(token):
    decoded_token = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    return decoded_token


def get_name_and_login_from_decrypt_token(request: Request):
    token = request.cookies.get("access_token")
    token_type = request.cookies.get("token_type")
    if token_type == "bearer" and token:
        decoded_token = get_params_from_decrypt_token(token)
        name = decoded_token.get("name")
        login = decoded_token.get("login", "False")
    else:
        name = None
        login = False
    return name, login

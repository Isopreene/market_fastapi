import jwt
from datetime import datetime, timedelta
import os, binascii
from passlib.context import CryptContext

SECRET_KEY = os.environ.get('SECRET_KEY', binascii.hexlify(os.urandom(24)))
ALGORITHM = os.environ.get('ALGORITHM', 'HS256')
ACCESS_TOKEN_EXPIRE_MINUTES = os.environ.get('ACCESS_TOKEN_EXPIRE_MINUTES', 30)
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


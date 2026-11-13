from datetime import datetime, timedelta, timezone
import jwt
from fastapi import HTTPException, status
from passlib.context import CryptContext

# argon2 pentru parole
pwd_context = CryptContext(schemes=['argon2'], deprecated='auto')

SECRET_KEY = '673ed643db70aee6c3a3de0350ec4ec9a808b33e2424cb4a0c63a58393323803'
ALGORITHM = 'HS256'

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def create_password_reset_token(email: str) -> str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    payload = {
        'sub': email,
        'exp': expire,
        'type': 'password_reset'
    }

    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def verify_password_reset_token(token: str) -> str:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=ALGORITHM)
        if payload.get('type') != 'password_reset':
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Invalid token type')
        return payload.get('sub')
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Token expired')
    except jwt.PyJWTError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Invalid token')
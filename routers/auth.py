from datetime import datetime, timedelta, timezone
from typing import Optional
from fastapi import APIRouter, Request, Depends, Form, status, Response, BackgroundTasks, HTTPException
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from passlib.context import CryptContext
from jose import JWTError, jwt
from sqlalchemy import select
from sqlalchemy.orm import Session
import os
import resend

from slowapi import Limiter
from slowapi.util import get_remote_address

import models
from database import get_db
from dotenv import load_dotenv

load_dotenv()

router = APIRouter(tags=['Authentication'])
templates = Jinja2Templates(directory='templates')


SECRET_KEY = os.getenv('SECRET_KEY')
ALGORITHM = 'HS256'
ACCESS_TOKEN_EXPIRE_MINUTES = 30
RESEND_API_KEY = os.getenv('RESEND_API_KEY')


if not SECRET_KEY:
    raise ValueError('SECRET_KEY is not set in .env file!')

if RESEND_API_KEY:
    resend.api_key = RESEND_API_KEY

# limiter - rate limit requests
limiter = Limiter(key_func=get_remote_address)

# argon2
pwd_context = CryptContext(schemes=['argon2'], deprecated='auto')


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_hash_password(password):
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=15))
    to_encode.update({'exp': expire})

    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def create_password_reset_token(email: str) -> str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    payload = {
        'sub': email,
        'exp': expire,
        'type': 'password_reset'
    }

    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def verify_password_reset_token(token: str) -> Optional[str]:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        if payload.get('type') != 'password_reset':
            return None
        return payload.get('sub')

    except JWTError:
        return None


import os
import resend

resend.api_key = os.getenv('RESEND_API_KEY')

def send_reset_email(to_email: str, token: str):
    reset_url = f"http://localhost:8000/reset-password?token={token}"
    params = {
        "from": "Security Team <onboarding@resend.dev>",
        "to": [to_email],
        "subject": "Recuperare parolă - PostATodo",
        "html": f"""
            <p>Salut,</p>
            <p>Ai solicitat resetarea parolei pentru contul tău. Dă click pe linkul de mai jos pentru a continua:</p>
            <p><a href="{reset_url}">Resetează parola</a></p>
            <p>Dacă nu ai solicitat acest lucru, poți ignora acest email.</p>
        """
    }
    try:
        response = resend.Emails.send(params)
        print(f"Email trimis cu succes! Răspuns Resend: {response}")
    except Exception as e:
        print(f"Eroare la trimiterea emailului prin Resend: {e}")


def get_current_user(request: Request, db: Session = Depends(get_db)):
    token = request.cookies.get('access_token')

    if not token:
        return None

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get('sub')
        if username is None:
            return None

    except Exception as e:
        print(f"Debug error JWT : {e}")
        return None


    stmt = select(models.User).where(models.User.username == username)
    user = db.scalar(stmt)
    return user


@router.get('/login', include_in_schema=False)
def login_page(request: Request):
    return templates.TemplateResponse(request, 'login.html', {'title': 'Login'})


@router.post('/login', include_in_schema=False)
def login_user(request: Request, db: Session = Depends(get_db), username: str = Form(...), password: str = Form(...)):
    stmt = select(models.User).where(models.User.username == username)
    user = db.scalar(stmt)

    if not user or not verify_password(password, user.hashed_password):
        return templates.TemplateResponse(
            request,
            'login.html',
            {'title': 'Login', 'error': 'Invalid username or password'},
            status_code=status.HTTP_400_BAD_REQUEST
        )


    access_token = create_access_token(
        data = {'sub': user.username},
        expires_delta = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )

    response = RedirectResponse(url='/', status_code=status.HTTP_303_SEE_OTHER)
    response.set_cookie(key='access_token', value=access_token, httponly=True)

    return response

@router.get('/register', include_in_schema=False)
def register_page(request: Request):
    return templates.TemplateResponse(request, 'register.html', {'title': 'Register'})

@router.post('/register', include_in_schema=False)
def register_user(
    request: Request,
    db: Session = Depends(get_db),
    username: str = Form(...),
    email: str = Form(...),
    password: str = Form(...)
    ):

    stmt = select(models.User).where((models.User.username == username) | (models.User.email == email))

    if db.scalar(stmt):
        return templates.TemplateResponse(request, 'register.html', {'title': 'Register', 'error': 'Username or email already exist'})

    new_user = models.User(
        username = username,
        email = email, 
        hashed_password = get_hash_password(password)
    )

    db.add(new_user)
    db.commit()

    return RedirectResponse(url='/login', status_code=status.HTTP_303_SEE_OTHER)


@router.get('/change-password', include_in_schema=False)
def change_password_page(request: Request, current_user: models.User = Depends(get_current_user)):
    return templates.TemplateResponse(request, 'change_password.html', {'title': 'Change password', 'user': current_user})


@router.post('/change-password', include_in_schema=False)
def change_password_submit(
    request: Request,
    current_password: str = Form(...),
    new_password: str = Form(...),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):

    # check if password is correctly typed
    if not verify_password(current_password, current_user.hashed_password):
        return templates.TemplateResponse(
            request,
            'change_password.html',
            {'title': 'Change password', 'error': 'Incorrect password', 'user': current_user}
        )

    # update with new password
    current_user.hashed_password = get_hash_password(new_password)
    db.commit()

    return RedirectResponse(url='/', status_code=status.HTTP_303_SEE_OTHER)


@router.get('/forgot-password', include_in_schema=False)
def forgot_password_page(request: Request):
    return templates.TemplateResponse(request, 'forgot_password.html', {'title': 'Forgot Password'})

@router.post('/forgot-password', include_in_schema=False)
@limiter.limit('3/hour')
def forgot_password_submit(
    request: Request,
    background_tasks: BackgroundTasks,
    email: str = Form(...),
    db: Session = Depends(get_db)
    ):

    stmt = select(models.User).where(models.User.email == email)
    user = db.scalar(stmt)

    # enumeration prevention - we return same message even if the email exists or not in db
    
    message = "If the submited email address is part of our system we will send you a reset link."

    if user:
        token = create_password_reset_token(user.email)
        background_tasks.add_task(send_reset_email, user.email, token)
        print(f'DEBUG - s-a adaugat task-ul de email pentru {user.email}')

    return templates.TemplateResponse(
        request,
        'forgot_password.html',
        {'title': 'Forgot password', 'message': message}
    )

# 1. Ruta GET - Afișează formularul de resetare a parolei
@router.get('/reset-password', include_in_schema=False)
def reset_password_page(request: Request, token: str):
    return templates.TemplateResponse(request, 'reset_password.html', {'title': 'Resetează Parola', 'token': token})

# 2. Ruta POST - Procesează noua parolă trimisă din formular
@router.post('/reset-password', include_in_schema=False)
def reset_password_submit(
    request: Request, 
    token: str = Form(...), 
    password: str = Form(...), 
    db: Session = Depends(get_db)
):
    # Validăm token-ul JWT primit din formular
    email = verify_password_reset_token(token)
    if not email:
        return templates.TemplateResponse(request, 'reset_password.html', {'title': 'Resetează Parola', 'error': 'Token invalid sau expirat.'})

    # Căutăm utilizatorul în baza de date
    stmt = select(models.User).where(models.User.email == email)
    user = db.scalar(stmt)
    
    if not user:
        return templates.TemplateResponse(request, 'reset_password.html', {'title': 'Resetează Parola', 'error': 'Utilizatorul nu a fost găsit.'})

    # Actualizăm parola cu noul hash
    user.hashed_password = get_hash_password(password)
    db.commit()

    # Redirecționăm utilizatorul către login după succes
    return RedirectResponse(url='/login', status_code=status.HTTP_303_SEE_OTHER)

@router.get('/logout', include_in_schema=False)
def logout():
    resp = RedirectResponse(url='/login', status_code = status.HTTP_303_SEE_OTHER)
    resp.delete_cookie('access_token')
    return resp


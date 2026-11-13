from fastapi import FastAPI
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from routers.auth import limiter
from fastapi.staticfiles import StaticFiles

from database import engine, Base
from routers import auth, tasks


Base.metadata.create_all(bind=engine)

# app
app = FastAPI(title='Post a TODO App')

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)


# static files directory
app.mount('/static', StaticFiles(directory='static'), name='static')


# routers
app.include_router(auth.router)
app.include_router(tasks.router)


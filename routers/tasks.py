import models
from datetime import date as date_type
from typing import Optional
from fastapi import APIRouter, Request, HTTPException, status, Depends, Form, Query
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import select, extract
from sqlalchemy.orm import Session


from schemas import TaskCreate, TaskResponse, TaskUpdate
from database import get_db
from routers.auth import get_current_user


router = APIRouter(tags=['Tasks'])
templates = Jinja2Templates(directory='templates')

@router.get('/', include_in_schema=False)
@router.get('/tasks', include_in_schema=False)
def home(
    request: Request,
    db: Session = Depends(get_db),
    date: Optional[str] = Query(None),
    year: Optional[int] = Query(None),
    month: Optional[int] = Query(None)
):

    current_user = get_current_user(request, db)


    if not current_user:
        return RedirectResponse(url='/login', status_code=status.HTTP_303_SEE_OTHER)


    stmt = select(models.Task).where(models.Task.user_id == current_user.id)
    selected_date_str = date or 'All dates'

    if date:
        try:
            parsed_date = date_type.fromisoformat(date)
            stmt = stmt.where(models.Task.due_date == parsed_date)

        except ValueError:
            pass

    elif year and month:
        stmt = stmt.where(
            extract('year', models.Task.due_date) == year,
            extract('month', models.Task.due_date) == month
        )


    stmt = stmt.order_by(models.Task.id.desc())
    db_tasks = db.scalars(stmt).all()

    task_dates_stmt = select(models.Task.due_date).where(
        models.Task.user_id == current_user.id,
        models.Task.due_date.isnot(None)
    ).distinct()

    raw_task_dates = db.scalars(task_dates_stmt).all()
    task_dates = [d.isoformat() for d in raw_task_dates if d]

    return templates.TemplateResponse(
        request = request,
        name = 'home.html',
        context = {
            'tasks': db_tasks,
            'title': 'Dashboard',
            'selected_date': selected_date_str,
            'task_dates': task_dates,
            'user': current_user
        }
    )



@router.get('/tasks/{task_id}', include_in_schema=False)
def task_page(request: Request, task_id: int, db: Session = Depends(get_db)):
    current_user = get_current_user(request, db)
    if not current_user:
        return RedirectResponse(url='/login', status_code=status.HTTP_303_SEE_OTHER)

    stmt = select(models.Task).where(models.Task.id == task_id, models.Task.user_id == current_user.id)
    task = db.scalar(stmt)

    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Task not found')

    else:
        return templates.TemplateResponse(
            request = request,
            name = 'task.html',
            context = {
                'request': request,
                'task': task,
                'title': task.title[:20],
                'user': current_user,
            }
        )

@router.post('/task/{task_id}/edit', include_in_schema=False)
def edit_task_form(
    request: Request,
    task_id: int,
    db: Session = Depends(get_db),
    title: str = Form(...),
    description: str = Form(""),
    completed: bool = Form(False),
):
    current_user = get_current_user(request, db)

    if not current_user:
        return RedirectResponse(url='/login', status_code=status.HTTP_303_SEE_OTHER)

    stmt = select(models.Task).where(models.Task.id == task_id, models.Task.user_id == current_user.id)
    task = db.scalar(stmt)

    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Task not found')

    task.title = title
    task.description = description
    task.completed = completed

    db.commit()

    return RedirectResponse(url='/', status_code=status.HTTP_303_SEE_OTHER)




# API Routes
@router.get('/api/tasks', response_model=list[TaskResponse])
def get_tasks(request: Request, db: Session = Depends(get_db)):
    current_user = get_current_user(request, db)
    if not current_user:
        raise HTTPException(status_code=401, detail='Not authenticated!')

    # the query
    stmt = select(models.Task).where(models.Task.user_id == current_user.id)
    return db.scalars(stmt).all()


@router.post('/api/tasks', response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
def create_task(task_data: TaskCreate, request: Request, db: Session = Depends(get_db)):
    current_user = get_current_user(request, db)

    if not current_user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Not authenticated!')

    new_task = models.Task(**task_data.model_dump(), user_id = current_user.id)

    if not new_task.due_date:
        new_task.due_date = date_type.today()


    db.add(new_task)
    db.commit()
    db.refresh(new_task)
    return new_task



@router.patch('/api/tasks/{task_id}', response_model=TaskResponse)
def update_task_status(task_id: int, task_update: TaskUpdate, request: Request, db: Session = Depends(get_db)):
    current_user = get_current_user(request, db)

    if not current_user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Not authenticated!')

    stmt = select(models.Task).where(models.Task.id == task_id, models.Task.user_id == current_user.id)
    task = db.scalar(stmt)

    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Task Not found')

    update_data = task_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(task, key, value)


    db.commit()
    db.refresh(task)
    return task


@router.delete('/api/tasks/{task_id}')
def delete_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):

    # search for task and verify is belonging to current user
    stmt = select(models.Task).where(models.Task.id == task_id, models.Task.user_id == current_user.id)
    task = db.scalar(stmt)

    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Task not found')

    db.delete(task)
    db.commit()

    return {'message': 'Task successfully deleted.'}


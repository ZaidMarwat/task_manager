# app/routers/tasks.py
from datetime import datetime
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session, select
from ..db import get_session
from ..models import Task, User
from ..schemas import TaskCreate, TaskRead, TaskUpdate
from ..deps import get_current_user

router = APIRouter(prefix="/tasks", tags=["tasks"])

@router.post("/", response_model=TaskRead, status_code=201)
def create_task(payload: TaskCreate, session: Session = Depends(get_session), user: User = Depends(get_current_user)):
    task = Task(**payload.model_dump(), owner_id=user.id)
    session.add(task)
    session.commit()
    session.refresh(task)
    return task

@router.get("/", response_model=list[TaskRead])
def list_tasks(
    session: Session = Depends(get_session),
    user: User = Depends(get_current_user),
    status: Optional[str] = Query(None),
    q: Optional[str] = Query(None, description="Search in title/description"),
    min_priority: int = Query(1, ge=1, le=5),
    max_priority: int = Query(5, ge=1, le=5),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
):
    stmt = select(Task).where(Task.owner_id == user.id)
    if status:
        stmt = stmt.where(Task.status == status)
    if q:
        like = f"%{q}%"
        stmt = stmt.where((Task.title.ilike(like)) | (Task.description.ilike(like)))
    stmt = stmt.where(Task.priority >= min_priority, Task.priority <= max_priority)
    stmt = stmt.order_by(Task.due_date.is_(None), Task.due_date, Task.priority)
    tasks = session.exec(stmt.offset(offset).limit(limit)).all()
    return tasks

@router.get("/{task_id}", response_model=TaskRead)
def get_task(task_id: int, session: Session = Depends(get_session), user: User = Depends(get_current_user)):
    task = session.get(Task, task_id)
    if not task or task.owner_id != user.id:
        raise HTTPException(status_code=404, detail="Task not found")
    return task

@router.patch("/{task_id}", response_model=TaskRead)
def update_task(task_id: int, payload: TaskUpdate, session: Session = Depends(get_session), user: User = Depends(get_current_user)):
    task = session.get(Task, task_id)
    if not task or task.owner_id != user.id:
        raise HTTPException(status_code=404, detail="Task not found")
    data = payload.model_dump(exclude_unset=True)
    for k, v in data.items():
        setattr(task, k, v)
    task.updated_at = datetime.utcnow()
    session.add(task)
    session.commit()
    session.refresh(task)
    return task

@router.delete("/{task_id}", status_code=204)
def delete_task(task_id: int, session: Session = Depends(get_session), user: User = Depends(get_current_user)):
    task = session.get(Task, task_id)
    if not task or task.owner_id != user.id:
        raise HTTPException(status_code=404, detail="Task not found")
    session.delete(task)
    session.commit()
    return None

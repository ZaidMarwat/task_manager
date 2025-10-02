# app/main.py
from fastapi import FastAPI
from .db import init_db
from .routers import auth as auth_router
from .routers import tasks as tasks_router

app = FastAPI(title="Task Manager API", version="1.0.0")

@app.on_event("startup")
def on_startup():
    init_db()

app.include_router(auth_router.router)
app.include_router(tasks_router.router)

# Swagger UI: /docs | ReDoc: /redoc

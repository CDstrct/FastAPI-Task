from fastapi import FastAPI, Depends, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from . import crud, models, schemas, database

app = FastAPI()

models.Base.metadata.create_all(bind=database.engine)

def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()
@app.post("/tasks", response_model=schemas.Task)
def create_task(task: schemas.TaskCreate, db: Session = Depends(get_db)):
    return crud.create_task(db=db, task=task)


tasks = []
pomodoro_sessions = []

class Task(BaseModel):
    id: int
    title: str
    description: Optional[str] = None
    status: str = "TODO"

class TaskCreate(BaseModel):
    title: str
    description: Optional[str] = None

class Pomodoro(BaseModel):
    task_id: int
    start_time: datetime
    end_time: datetime
    completed: bool

@app.get("/")
def read_root():
    return {"Welcome to the FastAPI Task and Pomodoro App!"}

@app.post("/tasks")
def create_task(task: TaskCreate):
    new_task = {
        "id": len(tasks) + 1,
        "title": task.title,
        "description": task.description,
        "status": "TODO",
    }
    tasks.append(new_task)
    return new_task

@app.get("/tasks")
def get_tasks():
    return tasks

@app.get("/tasks/{task_id}")
def get_task(task_id: int):
    task = next((task for task in tasks if task["id"] == task_id), None)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found.")
    return task

@app.put("/tasks/{task_id}")
def update_task(task_id: int, task: TaskCreate):
    existing_task = next((t for t in tasks if t["id"] == task_id), None)
    if not existing_task:
        raise HTTPException(status_code=404, detail="Task not found.")
    existing_task.update({"title": task.title, "description": task.description})
    return existing_task

@app.delete("/tasks/{task_id}")
def delete_task(task_id: int):
    global tasks
    tasks = [task for task in tasks if task["id"] != task_id]
    return {"message": "Task deleted successfully."}

@app.post("/pomodoro")
def create_pomodoro(task_id: int):
    task = next((task for task in tasks if task["id"] == task_id), None)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found.")
    new_session = {
        "task_id": task_id,
        "start_time": datetime.now(),
        "end_time": datetime.now() + timedelta(minutes=25),
        "completed": False,
    }
    pomodoro_sessions.append(new_session)
    return new_session

@app.post("/pomodoro/{task_id}/stop")
def stop_pomodoro(task_id: int):
    session = next((s for s in pomodoro_sessions if s["task_id"] == task_id and not s["completed"]), None)
    if not session:
        raise HTTPException(status_code=404, detail="Active Pomodoro session not found.")
    session["completed"] = True
    return {"message": "Pomodoro session stopped successfully."}

@app.get("/pomodoro/stats")
def get_pomodoro_stats():
    stats = {}
    for session in pomodoro_sessions:
        if session["completed"]:
            stats[session["task_id"]] = stats.get(session["task_id"], 0) + 1
    return {"completed_sessions": stats}

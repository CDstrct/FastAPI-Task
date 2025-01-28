from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from . import crud, models, schemas, database

app = FastAPI()

# Tworzenie tabel w bazie danych
models.Base.metadata.create_all(bind=database.engine)

def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Endpoint do tworzenia zadania
@app.post("/tasks", response_model=schemas.Task)
def create_task(task: schemas.TaskCreate, db: Session = Depends(get_db)):
    return crud.create_task(db=db, task=task)

# Endpoint do zatrzymania sesji Pomodoro
@app.post("/pomodoro/{task_id}/stop")
def stop_pomodoro(task_id: int, db: Session = Depends(get_db)):
    session = db.query(models.Pomodoro).filter(models.Pomodoro.task_id == task_id, models.Pomodoro.completed == False).first()
    if not session:
        raise HTTPException(status_code=404, detail="Active Pomodoro session not found.")
    session.completed = True
    db.commit()
    return {"message": "Pomodoro session stopped successfully."}

@app.on_event("startup")
async def startup():
    await database.connect()

@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()

# Inne endpointy
@app.get("/")
def read_root():
    return {"message": "Welcome to the FastAPI Task and Pomodoro App!"}

@app.get("/tasks")
def get_tasks(db: Session = Depends(get_db)):
    tasks = db.query(models.Task).all()
    return tasks

@app.get("/tasks/{task_id}")
def get_task(task_id: int, db: Session = Depends(get_db)):
    task = db.query(models.Task).filter(models.Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found.")
    return task

@app.put("/tasks/{task_id}")
def update_task(task_id: int, task: schemas.TaskCreate, db: Session = Depends(get_db)):
    existing_task = db.query(models.Task).filter(models.Task.id == task_id).first()
    if not existing_task:
        raise HTTPException(status_code=404, detail="Task not found.")
    existing_task.title = task.title
    existing_task.description = task.description
    db.commit()
    return existing_task

@app.delete("/tasks/{task_id}")
def delete_task(task_id: int, db: Session = Depends(get_db)):
    task = db.query(models.Task).filter(models.Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found.")
    db.delete(task)
    db.commit()
    return {"message": "Task deleted successfully."}

@app.post("/pomodoro")
def create_pomodoro(task_id: int, db: Session = Depends(get_db)):
    task = db.query(models.Task).filter(models.Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found.")
    new_session = models.Pomodoro(task_id=task_id, start_time=datetime.now(), end_time=datetime.now() + timedelta(minutes=25), completed=False)
    db.add(new_session)
    db.commit()
    db.refresh(new_session)
    return new_session
}

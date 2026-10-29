from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI(
    title="Task API",
    version="1.0.0",
)


class TaskCreate(BaseModel):
    title: str


class Task(TaskCreate):
    id: int
    completed: bool = False


tasks: dict[int, Task] = {}
next_id = 1


@app.get("/health")
def health_check():
    return {"status": "healthy"}


@app.post("/tasks", status_code=201)
def create_task(payload: TaskCreate):
    global next_id

    task = Task(id=next_id, title=payload.title)
    tasks[next_id] = task
    next_id += 1

    return task


@app.get("/tasks")
def list_tasks():
    return list(tasks.values())


@app.get("/tasks/{task_id}")
def get_task(task_id: int):
    task = tasks.get(task_id)

    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")

    return task
from fastapi import FastAPI, HTTPException
from course_catalog_scraper.scraper import scrape_course_catalog_data
from schedule_of_classes_scraper.soc_scraper import scrape_course_data_from_schedule_of_classes
import threading
from pydantic import BaseModel
from typing import List, Optional
from uuid import UUID, uuid4
from course_classes import Course

app = FastAPI()


@app.get("/")
def intro_page():
    return {"message": "Welcome to my UMD Courses API"}


@app.get("/classes/{course_number}", response_model=List[Course])
def course_data(course_number: str):
    """
    Create a new user with this route.
    Possible responses:
    201: New User Created
    400: Bad email id supplied.
    409: User already signed up, hence causing conflict with existing id.
    """

    return scrape_course_catalog_data(course_number)

@app.get("/classes/{course_number}/sections")
def section_data(course_number: str):
    courses_json = scrape_course_data_from_schedule_of_classes(course_number)
    if courses_json:
        return courses_json
    else:
        raise HTTPException(status_code=404, detail="Task not found",
                            headers={"X-Error": "There goes my error"})


# class Task(BaseModel):
#     id: Optional[UUID] = None
#     title: str
#     description: Optional[str] = None
#     completed: bool = False
#
# tasks = []
#
# @app.post("/tasks/", response_model=Task)
# def create_task(task: Task):
#     task.id = uuid4()
#     tasks.append(task)
#     return task
#
# @app.get("/tasks/", response_model=List[Task])
# def read_tasks():
#     return tasks
#
# @app.get("/tasks/{task_id}", response_model=Task)
# def read_task(task_id: UUID):
#     for task in tasks:
#         if task.id == task.id:
#             return task
#     raise HTTPException(status_code=404, detail="Task not found")
#
# @app.put("/tasks/{task_id}", response_model=Task)
# def update_task(task_id: UUID, task_update: Task):
#     for idx, task in enumerate(tasks):
#         if task.id == task_id:
#             updated_task = task.copy(update=task_update.dict(exclude_unset=True))
#             tasks[idx] = updated_task
#             return updated_task
#
#     raise HTTPException(status_code=404, detail="Task not found")
#
#
# @app.delete("/tasks/{task_id}", response_model=Task)
# def delete_task(task_id: UUID):
#     for idx, task in enumerate(tasks):
#         if task.id == task_id:
#             return tasks.pop(idx)
#
#     raise HTTPException(status_code=404, detail="Task not found")
#


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, port=8000)
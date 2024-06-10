from fastapi import FastAPI, HTTPException
from course_catalog_scraper.scraper import scrape_course_catalog_data
from schedule_of_classes_scraper.soc_scraper import scrape_course_data_from_schedule_of_classes
import threading
from pydantic import BaseModel
from typing import List, Optional
from uuid import UUID, uuid4
from course_classes import Course, Course_With_Section_Info
from gen_eds.main_gen_ed import all_gen_eds_scraper
from course_classes import Gen_Ed


app = FastAPI()


@app.get("/")
def intro_page():
    return {"message": "Welcome to my UMD Courses API"}


@app.get("/all_gen_eds", response_model=List[Gen_Ed])
def all_general_education_categories():
    """
    Gives a list of all the General Education requirements at the University of Maryland
    """
    all_gen_eds = all_gen_eds_scraper()

    if all_gen_eds:
        return all_gen_eds
    else:
        raise HTTPException(status_code=404, detail="Website might be down!")


@app.get("/classes/{course_number}", response_model=List[Course])
def course_data(course_number: str):
    """
    Gets course data
    """

    if len(course_number) < 4:
        raise HTTPException(status_code=404, detail="Course not found!")
    elif len(course_number) > 4:
        course_prefix = course_number[:4]
    else:
        course_prefix = course_number

    course_data = scrape_course_catalog_data(course_prefix, course_number)

    if course_data:
        return course_data
    else:
        raise HTTPException(status_code=404, detail="Course not found!")

@app.get("/class_sections/{course_number}/{term_id}/", response_model=List[List[Course_With_Section_Info]])
def section_data(term_id: str, course_number: str):
    courses_json = scrape_course_data_from_schedule_of_classes(term_id=term_id, course_acronym=course_number)
    if courses_json:
        return courses_json
    else:
        raise HTTPException(status_code=404, detail="Course not found!")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, port=8000)
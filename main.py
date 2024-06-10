from fastapi import FastAPI, HTTPException
from course_catalog_scraper.scraper import scrape_course_catalog_data
import course_prefixes_dataset_creation
from course_prefixes_dataset_creation.main_course_prefixes_scraper import update_umd_courses
from schedule_of_classes_scraper.soc_scraper import scrape_course_data_from_schedule_of_classes
import threading
from pydantic import BaseModel
from typing import List, Optional
from uuid import UUID, uuid4
from course_classes import Course, Course_With_Section_Info, Course_Prefix
from gen_eds.main_gen_ed import all_gen_eds_scraper
from course_classes import Gen_Ed

app = FastAPI()


@app.get("/")
def intro_page():
    return {"message": "Welcome to my UMD Courses API"}


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


# @app.get("/class_sections/{course_number}/{term_id}/", response_model=List[List[Course_With_Section_Info]])
# def section_data(term_id: str, course_number: str):
@app.get("/class_sections/{course_number}/", response_model=List[List[Course_With_Section_Info]])
def section_data(course_number: str):
    courses_json = scrape_course_data_from_schedule_of_classes(course_number)
    if courses_json:
        return courses_json
    else:
        raise HTTPException(status_code=404, detail="Course not found!")


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


@app.get("/course_prefixes", response_model=List[Course_Prefix])
def all_course_prefixes():
    """
    Gives a list of all the course prefixes at the University of Maryland
    """
    try:
        course_prefixes = update_umd_courses("./course_prefixes_dataset_creation/umd_course_prefixes.csv")

        if course_prefixes:
            return course_prefixes
        else:
            raise HTTPException(status_code=404, detail="Website might be down!")
    except:
        raise HTTPException(status_code=404, detail="Website might be down!")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, port=8000)

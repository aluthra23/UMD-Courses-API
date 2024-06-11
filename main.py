from fastapi import FastAPI, HTTPException, Query, Path
from course_catalog_scraper.scraper import scrape_course_catalog_data
from course_prefixes_dataset_creation.main_course_prefixes_scraper import update_umd_courses
from schedule_of_classes_scraper.soc_scraper import scrape_course_data_from_schedule_of_classes
from pydantic import BaseModel
from typing import List, Optional
from course_classes import Course, Course_With_Section_Info, Course_Prefix
from gen_eds.main_gen_ed import all_gen_eds_scraper
from course_classes import Gen_Ed
from term_id_functions import check_term_id, update_term_id

app = FastAPI(
    title="UMD Courses API",
    version="1.0.0",
    description="<p>Welcome to the UMD Courses API, an API that provides information about courses at the University of Maryland."
                "</p><p>This API allows users to:</p>"
                "<ul>"
                "<li>Retrieve course details</li>"
                "<li>Access section details for courses for specified semesters</li>"
                "<li>Get a list of all course prefixes and general education requirements</li>"
                "</ul>"
                "<p>This API retrieves the data by web scraping two critical websites in real-time: the "
                "<a href='https://app.testudo.umd.edu/soc/' target='blank'>Schedule of Classes</a>"
                " and the <a href='https://academiccatalog.umd.edu/' target='blank'>Course Catalog</a> websites "
                "provided by the University of Maryland.</p>"
                "<p>This API does not require any authentication but please be respectful of the UMD websites and "
                "don't load this API with too many requests.</p>"
                "<h4>Go to the <a href='/docs' target='blank'>Swagger</a> page or '/docs' if you want to see this API in action!</h4>"
                "<h4>Feel free to use this API and here's the <a href='https://github.com/aluthra23/UMD-Courses-API' target='blank'>Github Repository</a>!</h4>"
                "<h3>My Relevant Work related to this API: </h3>"
                "<p>I have constructed datasets about UMD courses using the webscraper mentioned above, which can be found in this <a "
                "href='https://github.com/aluthra23/UMD_Schedule_Web_Scraper' target='blank'>GitHub Repository</a>.</p>"
                "<p>I have also built a <a ""href='https://umd-chat-bot.streamlit.app/' target='blank'>chat bot</a> "
                "using the constructed datasets, which answers any questions students "
                "may have about coursework offered at UMD. To learn more about the technical details, here's the <a "
                "href='https://github.com/aluthra23/UMD-Scheduling-Chat-Bot' target='blank'>GitHub Repository</a>.</p>"
                "<p>Feel free to visit the links above, my <a href='https://aluthra23.github.io/personal-website/' "
                "target='blank'>website</a>, and my <a href=https://github.com/aluthra23 target='blank'>GitHub</a>!</p>",

    contact={
        "name": "Email",
        "email": "aravluthra@gmail.com"},
    redoc_url="/",
)


class Welcome(BaseModel):
    message: str

    def __init__(self, message: str):
        super().__init__(message=message)
        self.message = message


@app.get("/v1/classes/{course_number}", response_model=List[Course],
         responses={404: {"description": "Course not found!"}},
         description="Gets course data for a specific course offered at UMD or a list of courses that match the input course number. "
                     "Scrapes data from UMD's <a href='https://academiccatalog.umd.edu/' target='blank'>Course Catalog</a> website."
         )
async def get_course_data(
        course_number: str = Path(description="The level/designation of a UMD course, e.g., CMSC131"),
):
    """
    Gets course data for a specific course offered at UMD or a list of courses that match the input course number.
    """

    if len(course_number) < 4:
        raise HTTPException(status_code=404, detail="No such course exists! A course must have at least 4 characters.")

    course_prefix = course_number[:4]

    individual_course_data = scrape_course_catalog_data(course_prefix, course_number)

    if individual_course_data:
        return individual_course_data
    else:
        raise HTTPException(status_code=404, detail="Course not found!")


@app.get("/v1/class_sections/{course_number}", response_model=List[Course_With_Section_Info],
         responses={404: {"description": "Course not found!"}},
         description="Lists the sections of a specific course offered at UMD and other relevant course data, "
                     "or gets a list "
                     "of courses with the respective section data that match the inputted course number. Specifying the "
                     "term id or semester is optional and defaults to the current/upcoming semester. Scrapes data "
                     "from UMD's "
                     "<a href='https://app.testudo.umd.edu/soc/' target='blank'>Schedule of Classes</a> website.")
async def get_courses_and_section_data(
        course_number: str = Path(description="The level/designation of a UMD course, e.g., CMSC131"),
        term_id: str = Query(update_term_id(),
                             description="The semester the course takes place in YYYYMM format, e.g.,  "
                                         "202408 (Fall 2022). If not provided, the current/upcoming semester is used.")
):
    """
    Gets course section data for a specific course offered at UMD or a list of courses that match the input course number.

    :param course_number:
    :param term_id:
    :return:
    """

    if term_id and term_id != update_term_id():
        check_term_id(term_id)

        courses_json = scrape_course_data_from_schedule_of_classes(course_number, term_id)
    else:
        courses_json = scrape_course_data_from_schedule_of_classes(course_number)

    if courses_json:
        return courses_json
    else:
        raise HTTPException(status_code=404, detail="Course not found!")


@app.get("/v1/geneds", response_model=List[Gen_Ed],
         description="Gives a list of all the General Education requirements at the University of Maryland. Scrapes "
                     "data from UMD's <a href='https://app.testudo.umd.edu/soc/' target='blank'>Schedule of "
                     "Classes</a> website."
         )
async def get_all_general_education_categories():
    """
    Gives a list of all the General Education requirements at the University of Maryland
    """

    try:
        all_gen_eds = all_gen_eds_scraper()

        if all_gen_eds:
            return all_gen_eds
        else:
            raise HTTPException(status_code=503, detail="Server Issues: UMD Websites are currently unavailable")
    except:
        raise HTTPException(status_code=503, detail="Server Issues: UMD Websites are currently unavailable")


@app.get("/v1/course_prefixes", response_model=List[Course_Prefix],
         description="Gives a list of all the course prefixes at the University of Maryland. Scrapes data from UMD's "
                     "<a href='https://academiccatalog.umd.edu/' target='blank'>Course Catalog</a> and "
                     "<a href='https://app.testudo.umd.edu/soc/' target='blank'>Schedule of Classes</a> websites."
         )
async def get_all_course_prefixes():
    """
    Gives a list of all the course prefixes at the University of Maryland
    """

    return update_umd_courses("./course_prefixes_dataset_creation/umd_course_prefixes.csv")


# if __name__ == "__main__":
#     import uvicorn
#
#     uvicorn.run(app, port=8000)

from fastapi import FastAPI
from course_catalog_scraper.scraper import scrape_course_catalog_data
from schedule_of_classes_scraper.soc_scraper import scrape_course_data_from_schedule_of_classes

app = FastAPI()

@app.get("/")
def read():
    return scrape_course_catalog_data("CMSC")

@app.get("/sections")
def scrape():
    return scrape_course_data_from_schedule_of_classes("CMSC351")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, port=8000)
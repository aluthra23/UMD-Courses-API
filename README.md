# UMD Courses API (1.0.0)

## Introduction

UMD-Courses-API is an open-source FastAPI service for University of Maryland (UMD) course data. It is hosted at <https://umd-courses-api-aluthra-705eb647.koyeb.app/>, with interactive Swagger docs at <a href="https://umd-courses-api-aluthra-705eb647.koyeb.app/docs" target="_blank" rel="noopener noreferrer">/docs</a>.

## Features

- Retrieve catalog details for a course, or for every course matching a partial course number.
- List a course's sections for a semester: instructors, seats, waitlist, meeting times, rooms, and delivery mode.
- List every course prefix and every general education (gen ed) category.

## Data sources

Every request scrapes UMD's websites live; there is no database:

- <a href="https://app.testudo.umd.edu/soc/" target="_blank" rel="noopener noreferrer">UMD Schedule of Classes (Testudo)</a>: sections and gen eds.
- [UMD Academic Catalog](https://academiccatalog.umd.edu/): undergraduate and graduate course details.

## Endpoints

All endpoints are prefixed with `/v1`.

| Endpoint | Returns |
| --- | --- |
| `GET /v1/classes/{course_number}` | Catalog entries matching the course number, e.g. `CMSC131`, or `CMSC1` for every CMSC 100-level course. |
| `GET /v1/class_sections/{course_number}?term_id={term_id}` | Sections for the matching courses in one semester. |
| `GET /v1/geneds` | Every gen-ed category. |
| `GET /v1/course_prefixes` | Every course prefix and its full name. |

### Term IDs

`term_id` has the format `YYYY01` (spring) or `YYYY08` (fall), for example `202701` for Spring 2027. When it is omitted, the API uses the current or upcoming semester, worked out on every request:

- January 1 – February 20: that year's spring term.
- February 21 – September 30: that year's fall term.
- October 1 – December 31: next year's spring term.

### Errors

| Status | Meaning |
| --- | --- |
| `400` | Invalid term ID. |
| `404 {"detail": "Course not found!"}` | No matching course, or the semester has not been published yet. |
| `503` | UMD's websites could not be reached after several retries. |

## Used by the UMD Scheduling Chatbot

The [chatbot's data pipeline](https://github.com/aluthra23/UMD-Scheduling-Chat-Bot) calls `/v1/class_sections/CMSC351?term_id=…` to detect when a new semester is published. It treats the exact `404 {"detail": "Course not found!"}` response as "not published yet". Keep that response unchanged.

The pipeline and this API share their scraping helpers. `helping_files/helper.py`, `helping_files/http_utils.py`, and `course_prefixes_dataset_creation/course_prefixes_scraper.py` are identical in both repositories and should be changed together. The Schedule of Classes scrapers parse Testudo the same way but return different output (API models here, CSV rows there).

## Implementation

- **Scraping:** Requests and BeautifulSoup. Every request to UMD goes through `helping_files/http_utils.fetch`, which retries timeouts, connection errors, 429s, and 5xx responses before giving up with a 503.
- **API framework:** FastAPI, with responses validated by the Pydantic models in `course_classes.py`.
- **Deployment:** Koyeb's free tier. The first request after a period of inactivity can take a while while the instance wakes up.

## Local setup

The pinned requirements need Python 3.11 or newer.

```bash
python -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/uvicorn main:app --port 8000
```

## Tests

```bash
.venv/bin/python -m pip install httpx
PYTHONPATH=. .venv/bin/python -m unittest discover -s tests
```

## Notes

- This API does not require authentication.
- Please be respectful of UMD's websites and avoid sending too many requests.

## License

This project is open-source and available under the [MIT License](LICENSE).

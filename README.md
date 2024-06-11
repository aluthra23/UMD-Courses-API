# UMD-Courses-API

## Introduction

UMD-Courses-API is an open-source API developed using the FastAPI web framework. This API provides direct access to data related to University of Maryland (UMD) coursework. The API and its documentation can be accessed [here](https://umd-courses-api-aluthra-705eb647.koyeb.app/).

## Features

This API allows users to:
- Retrieve course details
- Access section details for courses for specified semesters
- Get a list of all course prefixes and general education requirements

## Data Sources

The API retrieves data by web scraping two critical UMD websites in real-time:
- <a href="https://app.testudo.umd.edu/soc/" target="_blank" rel="noopener noreferrer">UMD Schedule of Classes</a>
- [UMD Course Catalog](https://academiccatalog.umd.edu/)

## Implementation

### Web Scraper
The data is gathered using a web scraper built with the BeautifulSoup and Requests libraries.

### API Framework
FastAPI is used to handle user requests efficiently. Users can request specific data, and the server responds instantly with the relevant information.

### Deployment
The API is deployed on Koyeb using its free tier, making it accessible at any time. All endpoints are prefixed with `/v1` to standardize access. This prefix will be updated with future versions.

## Usage

Access the API at [UMD-Courses-API](https://umd-courses-api-aluthra-705eb647.koyeb.app/).

### Example Endpoints
- **Retrieve course details:** `/v1/courses/{course_id}`
- **Access section details:** `/v1/sections/{course_id}/{semester}`
- **List course prefixes and general education requirements:** `/v1/prefixes`

### Versioning
The current version is 1.0.0. Updates to the API and the README will be made with each new release.

## Notes

- This API does not require any authentication.
- Please be respectful of the UMD websites and avoid overloading the API with too many requests.

## License

This project is open-source and available under the [MIT License](LICENSE).

from bs4 import BeautifulSoup
from helping_files import helper, http_utils
from course_classes import Course
from typing import List

CATALOG_URLS = (
    "https://academiccatalog.umd.edu/undergraduate/approved-courses/",
    "https://academiccatalog.umd.edu/graduate/courses/",
)


def scrape_course_catalog_data(course_acronym, specific_course_number) -> List[Course]:
    """Undergraduate and graduate catalog entries matching the course number. Raises on network/HTTP failures."""
    course_acronym = course_acronym.lower().strip()
    courses_arr = []
    used_courses = set()

    for base_url in CATALOG_URLS:
        response = http_utils.fetch(f"{base_url}{course_acronym}/", allow_not_found=True)
        if response is None:
            continue
        soup = BeautifulSoup(response.text, 'html.parser')
        new_courses, used_courses = scrape_courses(soup.find_all('div', class_='courseblock'), course_acronym,
                                                   specific_course_number, used_courses)
        courses_arr.extend(new_courses)

    return courses_arr


def scrape_courses(courses, course_acronym, specific_course_number, used_courses: set) -> tuple[list[Course], set]:
    courses_arr = []

    for course_block in courses:
        course_dict = {
            "COURSE NUMBER": None,
            "NAME": None,
            "CREDITS": None,
            "DESCRIPTION": None,
            "PREREQUISITE": None,
            "RESTRICTION": None,
            "FORMERLY NAMED": None,
            "RECOMMENDED": None,
            "CREDIT ONLY GRANTED FOR": None,
            "REPEATABLE TO": None,
            "CROSS-LISTED": None,
            'COREQUISITE': None
            # Add more keys for other miscellaneous data if needed
        }

        title = course_block.find('p', class_='courseblocktitle noindent')
        if title is None or title.strong is None:
            continue
        course_dict["COURSE NUMBER"], course_dict["NAME"], course_dict["CREDITS"] = helper.parse_course_string(
            title.strong.text.strip())

        if course_dict["COURSE NUMBER"] in used_courses:
            continue

        if specific_course_number.upper() not in course_dict["COURSE NUMBER"]:
            continue

        description = helper.text_of(course_block, 'p', 'courseblockdesc noindent')
        course_dict["DESCRIPTION"] = description.replace("\n", "") if description else None

        extras = course_block.find_all('p', class_='courseblockextra noindent')
        for extra in extras:
            extra_description = extra.text
            label, description = helper.parse_extra(extra_description)

            if course_dict["CROSS-LISTED"]:
                course_dict[label.upper()] = helper.remove_period_end(description)
            else:
                course_dict[label.upper()], course_dict["CROSS-LISTED"] = (
                    helper.string_without_delimiter(helper.remove_period_end(description), "Cross-listed with"))

        course_info = Course(
            course_dict["COURSE NUMBER"],
            course_dict["NAME"],
            course_dict["CREDITS"],
            course_dict["DESCRIPTION"],
            course_dict["PREREQUISITE"],
            course_dict["RESTRICTION"],
            course_dict["FORMERLY NAMED"],
            course_dict["RECOMMENDED"],
            course_dict["CREDIT ONLY GRANTED FOR"],
            course_dict["REPEATABLE TO"],
            course_dict["CROSS-LISTED"],
            course_dict["COREQUISITE"]

        )
        courses_arr.append(course_info)
        used_courses.add(course_dict["COURSE NUMBER"])

    return courses_arr, used_courses

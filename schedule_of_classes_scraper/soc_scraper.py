from typing import List, Optional

from bs4 import BeautifulSoup

from course_classes import Course_Time, Course_With_Section_Info
from helping_files import helper, http_utils
from term_id_functions import update_term_id

base_url = "https://app.testudo.umd.edu/soc/search"


def find_message_div(time):
    message_divs = time.find_all('div', class_=lambda x: x and 'class' in x.lower())
    if message_divs:
        return message_divs[0].text.strip()
    return None


def clean_description(description: Optional[str]) -> Optional[str]:
    return description.replace("\n", "") if description else description


def scrape_course_data_from_schedule_of_classes(course_acronym: str, term_id: Optional[str] = None) -> List[Course_With_Section_Info]:
    """Scrape Testudo for every course matching course_acronym. Raises on network/HTTP failures."""
    term_id = term_id or update_term_id()
    url = f"{base_url}?courseId={course_acronym}&sectionId=&termId={term_id}&_openSectionsOnly=on&creditCompare=%3E%3D&credits=0.0&courseLevelFilter=ALL&instructor=&_facetoface=on&_blended=on&_online=on&courseStartCompare=&courseStartHour=&courseStartMin=&courseStartAM=&courseEndHour=&courseEndMin=&courseEndAM=&teachingCenter=ALL&_classDay1=on&_classDay2=on&_classDay3=on&_classDay4=on&_classDay5=on"

    response = http_utils.fetch(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    all_courses = []
    for course in soup.find_all('div', class_='course'):
        course_number = helper.text_of(course, 'div', 'course-id')
        if not course_number:
            continue

        section_title = helper.text_of(course, 'span', 'course-title')
        section_min_credits = helper.parse_int(helper.text_of(course, 'span', 'course-min-credits'))
        section_max_credits = helper.parse_int(helper.text_of(course, 'span', 'course-max-credits'))
        if section_max_credits is None:
            section_max_credits = section_min_credits
        section_grading = helper.text_of(course, 'span', 'grading-method')

        description_fields = {
            "GEN_EDS FULFILLED": "",
            "PREREQUISITE": None,
            "COREQUISITE": None,
            "RESTRICTION": None,
            "CREDIT ONLY GRANTED FOR": None,
            "FORMERLY": None,
            "RECOMMENDED": None,
            "CROSS-LISTED WITH": None,
            "DESCRIPTION": None,
        }

        if course.find('div', class_='approved-course-texts-container'):
            for description in course.find_all('div', class_='approved-course-text'):
                description_fields = helper.extract_course_details(html_content=str(description),
                                                                   existing_dict=description_fields,
                                                                   actual_html=description)

        descriptions = course.find('div', class_='course-texts-container')
        if descriptions:
            description_fields = helper.extract_abnormal_course_details(existing_dict=description_fields,
                                                                        actual_html=descriptions)

        gen_eds = course.find('div', class_='gen-ed-codes-group six columns')
        if gen_eds and str(gen_eds.text).strip():
            description_fields["GEN_EDS FULFILLED"] = helper.remove_all_whitespace(gen_eds.text.strip())

        shared = dict(section_title=section_title, section_min_credits=section_min_credits,
                      section_max_credits=section_max_credits, section_grading=section_grading,
                      description_fields=description_fields)
        classes = update_classes_data(course_number, term_id, course.find_all('div', class_='section delivery-f2f'),
                                      class_setting="NORMAL", **shared)
        classes += update_classes_data(course_number, term_id, course.find_all('div', class_='section delivery-blended'),
                                       class_setting="BLENDED", **shared)
        classes += update_classes_data(course_number, term_id, course.find_all('div', class_='section delivery-online'),
                                       class_setting="ONLINE", **shared)

        if not classes:
            classes = [
                Course_With_Section_Info(
                    course_number, section_title, term_id, section_min_credits, section_max_credits,
                    section_grading, description_fields["GEN_EDS FULFILLED"],
                    None, None, None, None, None, [], None, None, None, None,
                    description_fields["PREREQUISITE"], description_fields["COREQUISITE"],
                    description_fields["RESTRICTION"], description_fields["CREDIT ONLY GRANTED FOR"],
                    description_fields["FORMERLY"], description_fields["RECOMMENDED"],
                    description_fields["CROSS-LISTED WITH"], clean_description(description_fields["DESCRIPTION"]),
                )
            ]

        all_courses += classes

    return all_courses


def update_classes_data(course_number, term_id, open_sections, class_setting, section_title, section_min_credits,
                        section_max_credits, section_grading, description_fields) -> List[Course_With_Section_Info]:
    data = []

    for section in open_sections:
        section_id = helper.text_of(section, 'span', 'section-id')
        if not section_id:
            continue

        is_normal = 1 if class_setting in ("NORMAL", "BLENDED") else 0
        is_online = 1 if class_setting in ("ONLINE", "BLENDED") else 0
        is_blended = 1 if class_setting == "BLENDED" else 0

        instructors = [span.text.strip() for span in section.find_all('span', class_='section-instructor') if span.text.strip()]

        times_container = section.find('div', class_="class-days-container")
        all_times = []
        for time in (times_container.find_all('div', class_='row') if times_container else []):
            days = helper.text_of(time, 'span', 'section-days')
            if days:
                start_time = helper.text_of(time, 'span', 'class-start-time')
                end_time = helper.text_of(time, 'span', 'class-end-time')
                if "TBA" in days.upper() or not (start_time and end_time):
                    class_time = days
                else:
                    class_time = f"{days} {start_time}-{end_time}"
            else:
                class_time = find_message_div(time) or "No class message found"

            class_type = helper.text_of(time, 'div', 'two columns')
            class_type = class_type.upper() if class_type else "LECTURE"

            room = time.find('span', class_='class-building')
            if room:
                building = helper.text_of(room, 'span', 'building-code')
                if building:
                    room_number = helper.text_of(room, 'span', 'class-room')
                    room = f"{building} {room_number}" if room_number else building
                else:
                    room = room.text.strip()

            all_times.append(Course_Time(class_type, class_time, room))

        special_restriction = None
        restrictions = section.find('div', class_="section-texts-container")
        if restrictions:
            lines = []
            for restriction in restrictions.find_all('div', class_='section-text'):
                link = helper.extract_link_from_html(str(restriction))
                lines.append(f"{restriction.text}: {link}" if link else restriction.text)
            special_restriction = "\n".join(lines)

        data.append(Course_With_Section_Info(
            course_number,
            section_title,
            term_id,
            section_min_credits,
            section_max_credits,
            section_grading,
            description_fields["GEN_EDS FULFILLED"],
            section_id,
            ", ".join(instructors) or None,
            helper.parse_int(helper.text_of(section, 'span', 'total-seats-count')),
            helper.parse_int(helper.text_of(section, 'span', 'open-seats-count')),
            helper.parse_int(helper.text_of(section, 'span', 'waitlist-count')) or 0,
            all_times,
            is_normal,
            is_blended,
            is_online,
            special_restriction,
            description_fields["PREREQUISITE"],
            description_fields["COREQUISITE"],
            description_fields["RESTRICTION"],
            description_fields["CREDIT ONLY GRANTED FOR"],
            description_fields["FORMERLY"],
            description_fields["RECOMMENDED"],
            description_fields["CROSS-LISTED WITH"],
            clean_description(description_fields["DESCRIPTION"]),
        ))

    return data

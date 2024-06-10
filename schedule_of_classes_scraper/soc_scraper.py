from typing import List
import requests
from bs4 import BeautifulSoup
from fastapi import HTTPException
from course_classes import Course_Time, Course_With_Section_Info
from helping_files import helper

# Base URL for the UMD schedule of classes search
base_url = "https://app.testudo.umd.edu/soc/search"


def scrape_course_data_from_schedule_of_classes(course_acronym: str, term_id: str = "202408") -> List[List[Course_With_Section_Info]]:
    url = f"{base_url}?courseId={course_acronym}&sectionId=&termId={term_id}&_openSectionsOnly=on&creditCompare=%3E%3D&credits=0.0&courseLevelFilter=ALL&instructor=&_facetoface=on&_blended=on&_online=on&courseStartCompare=&courseStartHour=&courseStartMin=&courseStartAM=&courseEndHour=&courseEndMin=&courseEndAM=&teachingCenter=ALL&_classDay1=on&_classDay2=on&_classDay3=on&_classDay4=on&_classDay5=on"

    # Fetch the web page
    response = requests.get(url)
    if response.status_code != 200:
        # print(f"Failed to fetch data for {course_acronym}")
        raise HTTPException(status_code=400, detail="couldn't find course")

    # Parse the HTML content
    soup = BeautifulSoup(response.text, 'html.parser')

    courses = soup.find_all('div', class_='course')

    all_courses = []
    for course in courses:
        course_number = course.find('div', class_='course-id').text.strip()

        section_title = course.find('span', class_='course-title').text.strip()

        section_min_credits = course.find('span', class_='course-min-credits')
        if section_min_credits:
            section_min_credits = int(section_min_credits.text.strip())

            section_max_credits = course.find('span', class_='course-max-credits')
            if section_max_credits:
                section_max_credits = int(section_max_credits.text.strip())
            else:
                section_max_credits = section_min_credits

        section_grading = str(course.find('span', class_='grading-method').text).strip()

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

        descriptions = course.find('div', class_='approved-course-texts-container')
        if descriptions:
            descriptions = course.find_all('div', class_='approved-course-text')

            for description in descriptions:
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

        open_sections = course.find_all('div', class_='section delivery-f2f')
        classes = update_classes_data(course_number, term_id, open_sections,
                                      class_setting="NORMAL",
                                      section_title=section_title,
                                      section_min_credits=section_min_credits,
                                      section_max_credits=section_max_credits,
                                      section_grading=section_grading,
                                      description_fields=description_fields)

        # Blended Classes
        open_sections = course.find_all('div', class_='section delivery-blended')
        classes += update_classes_data(course_number, term_id, open_sections,
                                       class_setting="BLENDED",
                                       section_title=section_title,
                                       section_min_credits=section_min_credits,
                                       section_max_credits=section_max_credits,
                                       section_grading=section_grading,
                                       description_fields=description_fields)

        # Online Classes
        open_sections = course.find_all('div', class_='section delivery-online')
        classes += update_classes_data(course_number, term_id, open_sections,
                                       class_setting="ONLINE",
                                       section_title=section_title,
                                       section_min_credits=section_min_credits,
                                       section_max_credits=section_max_credits,
                                       section_grading=section_grading,
                                       description_fields=description_fields)

        if not classes:
            classes = []
            classes.append(
                Course_With_Section_Info(
                    course_number,
                    section_title,
                    term_id,
                    section_min_credits,
                    section_max_credits,
                    section_grading,
                    description_fields["GEN_EDS FULFILLED"],
                    None,
                    None,
                    None,
                    None,
                    None,
                    [],
                    None,
                    None,
                    None,
                    None,
                    description_fields["PREREQUISITE"],
                    description_fields["COREQUISITE"],
                    description_fields["RESTRICTION"],
                    description_fields["CREDIT ONLY GRANTED FOR"],
                    description_fields["FORMERLY"],
                    description_fields["RECOMMENDED"],
                    description_fields["CROSS-LISTED WITH"],
                    description_fields["DESCRIPTION"]
                )
            )


        all_courses.append(classes)

    return all_courses


def update_classes_data(course_number, term_id, open_sections, class_setting, section_title, section_min_credits,
                        section_max_credits, section_grading, description_fields) -> List[Course_With_Section_Info]:
    data = []

    for section in open_sections:
        section_data = {
            "COURSE NUMBER": course_number,
            "COURSE TITLE": section_title,
            "SEMESTER": term_id,
            "MINIMUM CREDITS": section_min_credits,
            "MAXIMUM CREDITS": section_max_credits,
            "GRADING METHOD": section_grading,
            "GEN_EDS FULFILLED": description_fields["GEN_EDS FULFILLED"],
            "SECTION ID": None,
            "INSTRUCTOR": None,
            "TOTAL SEATS": None,
            "OPEN SEATS": None,
            "WAITLIST COUNT": None,
            "CLASS TIMES": [],
            "IS NORMAL": 0,
            "IS BLENDED (NORMAL AND ONLINE)": 0,
            "IS ONLINE": 0,
            "SPECIAL RESTRICTION": None,
            "PREREQUISITE": description_fields["PREREQUISITE"],
            "COREQUISITE": description_fields["COREQUISITE"],
            "RESTRICTION": description_fields["RESTRICTION"],
            "CREDIT ONLY GRANTED FOR": description_fields["CREDIT ONLY GRANTED FOR"],
            "FORMERLY": description_fields["FORMERLY"],
            "RECOMMENDED": description_fields["RECOMMENDED"],
            "CROSS-LISTED WITH": description_fields["CROSS-LISTED WITH"],
            "DESCRIPTION": description_fields["DESCRIPTION"],
        }

        if class_setting == 'NORMAL':
            section_data["IS NORMAL"] = 1
        elif class_setting == 'ONLINE':
            section_data["IS ONLINE"] = 1
        else:
            section_data["IS NORMAL"] = 1
            section_data["IS ONLINE"] = 1
            section_data["IS BLENDED (NORMAL AND ONLINE)"] = 1

        section_id = str(section.find('span', class_='section-id').text).strip()
        section_data["SECTION ID"] = section_id

        section_instructors = section.find_all('span', class_='section-instructor')

        if len(section_instructors) > 1:
            instructors = ""
            for i, section_instructor in enumerate(section_instructors):
                instructors += str(section_instructor.text).strip()

                if i + 1 != len(section_instructors):
                    instructors += ", "

            section_data["INSTRUCTOR"] = instructors
        else:
            section_instructor = str(section.find('span', class_='section-instructor').text).strip()
            section_data["INSTRUCTOR"] = section_instructor

        total_seats = str(section.find('span', class_='total-seats-count').text).strip()
        section_data["TOTAL SEATS"] = int(total_seats)

        open_seats = str(section.find('span', class_='open-seats-count').text).strip()
        section_data["OPEN SEATS"] = int(open_seats)

        waitlist_seats = str(section.find('span', class_='waitlist-count').text).strip()
        section_data["WAITLIST COUNT"] = int(waitlist_seats)

        times = section.find('div', class_="class-days-container")
        times = times.find_all('div', class_='row')

        all_times = []
        # Iterating through class-days-container
        for i, time in enumerate(times):
            days = time.find('span', class_='section-days')
            has_specific_time = False
            start_time = ""
            end_time = ""

            class_time = ""

            if days:
                days = days.text.strip()

                if str(days).upper().find("TBA") != -1:
                    class_time = days
                else:
                    start_time = time.find('span', class_='class-start-time').text.strip()
                    end_time = time.find('span', class_='class-end-time').text.strip()
                    class_time = f"{days} {start_time}-{end_time}"
            else:
                message = time.find('span', class_='elms-class-message')
                if message:
                    message = message.text.strip()
                else:
                    message = time.find('div', class_='push_one eight columns class-message')

                    if message:
                        message = message.text.strip()
                    else:
                        message = time.find('div', class_='push_two eight columns class-message').text.strip()

                class_time = message

            class_type = time.find('div', class_='two columns')

            if class_type:
                class_type = class_type.text.strip().upper()
            else:
                class_type = "LECTURE"

            room = time.find('span', class_='class-building')

            if room:
                building = room.find('span', class_='building-code')
                if building:
                    building = building.text.strip()
                    room_number = room.find('span', class_='class-room')

                    if room_number:
                        room_number = room_number.text.strip()
                        room = f"{building} {room_number}"
                    else:
                        room = building
                else:
                    room = room.text.strip()

            new_course_time = Course_Time(class_type, class_time, room)
            all_times.append(new_course_time)

        section_data["CLASS TIMES"] = all_times

        # Iterating through section-texts-container
        restrictions = section.find('div', class_="section-texts-container")

        if restrictions:
            restrictions = restrictions.find_all('div', class_='section-text')

            full_restriction = ""
            for i, restriction in enumerate(restrictions):
                link = helper.extract_link_from_html(str(restriction))

                new_line = "\n"

                if i + 1 == len(restrictions):
                    new_line = ""

                if link:
                    full_restriction += f"{restriction.text}: {link}{new_line}"
                else:
                    full_restriction += f"{restriction.text}{new_line}"

            section_data["SPECIAL RESTRICTION"] = full_restriction

        course_data = Course_With_Section_Info(
            section_data["COURSE NUMBER"],
            section_data["COURSE TITLE"],
            section_data["SEMESTER"],
            section_data["MINIMUM CREDITS"],
            section_data["MAXIMUM CREDITS"],
            section_data["GRADING METHOD"],
            section_data["GEN_EDS FULFILLED"],
            section_data["SECTION ID"],
            section_data["INSTRUCTOR"],
            section_data["TOTAL SEATS"],
            section_data["OPEN SEATS"],
            section_data["WAITLIST COUNT"],
            section_data["CLASS TIMES"],
            section_data["IS NORMAL"],
            section_data["IS BLENDED (NORMAL AND ONLINE)"],
            section_data["IS ONLINE"],
            section_data["SPECIAL RESTRICTION"],
            section_data["PREREQUISITE"],
            section_data["COREQUISITE"],
            section_data["RESTRICTION"],
            section_data["CREDIT ONLY GRANTED FOR"],
            section_data["FORMERLY"],
            section_data["RECOMMENDED"],
            section_data["CROSS-LISTED WITH"],
            section_data["DESCRIPTION"]
        )

        data.append(course_data)

    return data

from pydantic import BaseModel
from typing import List, Optional


class Course(BaseModel):
    course_number: Optional[str]
    name: Optional[str]
    credits: Optional[str]
    description: Optional[str]
    prerequisite: Optional[str]
    restriction: Optional[str]
    formerly_named: Optional[str]
    recommended: Optional[str]
    credit_only_granted_for: Optional[str]
    repeatable_to: Optional[str]
    cross_listed: Optional[str]
    corequisite: Optional[str]

    def __init__(self, course_number: str, name: str, credits: str, description: str,
                 prerequisite: str, restriction: str, formerly_named: str, recommended: str,
                 credit_only_granted_for: str, repeatable_to: str, cross_listed: str, corequisite: str):
        super().__init__(course_number=course_number, name=name,
                         credits=credits, description=description, prerequisite=prerequisite,
                         restriction=restriction, formerly_named=formerly_named, recommended=recommended,
                         credit_only_granted_for=credit_only_granted_for, repeatable_to=repeatable_to,
                         cross_listed=cross_listed, corequisite=corequisite)

        self.course_number = course_number
        self.name = name
        self.credits = credits
        self.description = description
        self.prerequisite = prerequisite
        self.restriction = restriction
        self.formerly_named = formerly_named
        self.recommended = recommended
        self.credit_only_granted_for = credit_only_granted_for
        self.repeatable_to = repeatable_to
        self.cross_listed = cross_listed
        self.corequisite = corequisite


class Gen_Ed(BaseModel):
    gen_ed: Optional[str]
    full_form: Optional[str]

    def __init__(self, gen_ed: str, full_form: str):
        super().__init__(gen_ed=gen_ed, full_form=full_form)
        self.gen_ed = gen_ed
        self.full_form = full_form


class Course_Time(BaseModel):
    class_type: Optional[str]
    time: Optional[str]
    room: Optional[str]

    def __init__(self, class_type, time, room):
        super().__init__(class_type=class_type, time=time, room=room)
        self.class_type = class_type
        self.time = time
        self.room = room


class Course_With_Section_Info(BaseModel):
    course_number: Optional[str]
    course_title: Optional[str]
    semester: Optional[str]
    minimum_credits: Optional[int]
    maximum_credits: Optional[int]
    grading_method: Optional[str]
    gen_eds_fulfilled: Optional[str]
    section_id: Optional[str]
    instructor: Optional[str]
    total_seats: Optional[int]
    open_seats: Optional[int]
    waitlist_count: Optional[int]
    class_times: List[Course_Time]
    is_normal: Optional[int]
    is_blended: Optional[int]
    is_online: Optional[int]
    special_restriction: Optional[str]
    prerequisite: Optional[str]
    corequisite: Optional[str]
    restriction: Optional[str]
    credit_only_granted_for: Optional[str]
    formerly: Optional[str]
    recommended: Optional[str]
    cross_listed_with: Optional[str]
    description: Optional[str]

    def __init__(self, course_number: str, course_title: str, semester: str, minimum_credits: int,
                 maximum_credits: int, grading_method: str, gen_eds_fulfilled: str, section_id,
                 instructor, total_seats, open_seats, waitlist_count, class_times, is_normal, is_blended,
                 is_online, special_restriction, prerequisite: str, corequisite: str, restriction: str,
                 credit_only_granted_for: str, formerly: str, recommended: str, cross_listed_with: str,
                 description: str):
        super().__init__(course_number=course_number, course_title=course_title, semester=semester,
                         minimum_credits=minimum_credits, maximum_credits=maximum_credits,
                         grading_method=grading_method, gen_eds_fulfilled=gen_eds_fulfilled,
                         section_id=section_id, instructor=instructor, total_seats=total_seats,
                         open_seats=open_seats, waitlist_count=waitlist_count, class_times=class_times,
                         is_normal=is_normal, is_blended=is_blended, is_online=is_online,
                         special_restriction=special_restriction, prerequisite=prerequisite,
                         corequisite=corequisite, restriction=restriction,
                         credit_only_granted_for=credit_only_granted_for, formerly=formerly,
                         recommended=recommended, cross_listed_with=cross_listed_with,
                         description=description)

        self.course_number = course_number
        self.course_title = course_title
        self.semester = semester
        self.minimum_credits = minimum_credits
        self.maximum_credits = maximum_credits
        self.grading_method = grading_method
        self.gen_eds_fulfilled = gen_eds_fulfilled
        self.section_id = section_id
        self.instructor = instructor
        self.total_seats = total_seats
        self.open_seats = open_seats
        self.waitlist_count = waitlist_count
        self.class_times = class_times
        self.is_normal = is_normal
        self.is_blended = is_blended
        self.is_online = is_online
        self.special_restriction = special_restriction
        self.prerequisite = prerequisite
        self.corequisite = corequisite
        self.restriction = restriction
        self.credit_only_granted_for = credit_only_granted_for
        self.formerly = formerly
        self.recommended = recommended
        self.cross_listed_with = cross_listed_with
        self.description = description


class Course_Prefix(BaseModel):
    course_prefix: Optional[str]
    full_form: Optional[str]

    def __init__(self, course_prefix: str, full_form: str):
        super().__init__(course_prefix=course_prefix, full_form=full_form)
        self.course_prefix = course_prefix
        self.full_form = full_form

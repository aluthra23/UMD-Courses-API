from pydantic import BaseModel


class Course(BaseModel):
    course_prefix: str
    course_number: str
    name: str
    credits: str
    description: str
    prerequisite: str
    restriction: str
    formerly_named: str
    recommended: str
    credit_only_granted_for: str
    repeatable_to: str
    cross_listed: str
    corequisite: str

    def __init__(self, course_dict: dict):
        self.course_prefix = course_dict["COURSE PREFIX"]
        self.course_number = course_dict["COURSE NUMBER"]
        self.name = course_dict["NAME"]
        self.credits = course_dict["CREDITS"]
        self.description = course_dict["DESCRIPTION"]
        self.prerequisite = course_dict["PREREQUISITE"]
        self.restriction = course_dict["RESTRICTION"]
        self.formerly_named = course_dict["FORMERLY NAMED"]
        self.recommended = course_dict["RECOMMENDED"]
        self.credit_only_granted_for = course_dict["CREDIT ONLY GRANTED FOR"]
        self.repeatable_to = course_dict["REPEATABLE TO"]
        self.cross_listed = course_dict["CROSS-LISTED"]
        self.corequisite = course_dict["COREQUISITE"]

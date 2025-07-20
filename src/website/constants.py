from src.base.constants import BaseEnum


ACADEMIC_CALENDER_FILE_PATH = "website/calenders"
CAMPUS_REPORT_FILE_PATH = "website/reports"
CAMPUS_DOWNLOADS_FILE_PATH = "website/downloads"
STUDENT_CLUB_FILE_PATH = "website/clubs"
CAMPUS_UNION_FILE_PATH = "website/unions"
CAMPUS_KEY_OFFICIAL_FILE_PATH = "website/key-officials"


class ReportTypes(BaseEnum):
    SELF_STUDY = "SELF_STUDY"
    ANNUAL = "ANNUAL"
    OTHER = "OTHER"


class CampusEventTypes(BaseEnum):
    CULTURAL = "CULTURAL"
    TECHNICAL = "TECHNICAL"
    MUSICAL = "MUSICAL"
    SPORTS = "SPORTS"
    OTHER = "OTHER"

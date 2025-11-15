from src.base.constants import BaseEnum

CAMPUS_FILE_PATH = "website/files"
CAMPUS_KEY_OFFICIAL_FILE_PATH = "website/key-officials"
ACADEMIC_CALENDER_FILE_PATH = "website/calenders"
CAMPUS_REPORT_FILE_PATH = "website/reports"
CAMPUS_DOWNLOADS_FILE_PATH = "website/downloads"
CAMPUS_EVENT_FILE_PATH = "website/events"

CAMPUS_UNION_FILE_PATH = "website/unions"
CAMPUS_UNION_MEMBER_FILE_PATH = "website/unions/members"

STUDENT_CLUB_FILE_PATH = "website/clubs"
STUDENT_CLUB_MEMBER_FILE_PATH = "website/clubs/members"
STUDENT_CLUB_EVENT_FILE_PATH = "website/clubs"
CAMPUS_SECTION_FILE_PATH = "website/sections"
CAMPUS_UNIT_FILE_PATH = "website/units"
RESEARCH_FACILITY_FILE_PATH = "website/research-facilities"
GLOBAL_GALLERY_FILE_PATH = "website/global-gallery"
GLOBAL_EVENT_FILE_PATH = "website/global-events"


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

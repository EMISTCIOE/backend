from src.base.constants import BaseEnum


ACADEMIC_CALENDER_FILE_PATH = "website/calenders"
CAMPUS_REPORT_FILE_PATH = "website/reports"
CAMPUS_DOWNLOADS_FILE_PATH = "website/downloads"
STUDENT_CLUB_FILE_PATH = "website/clubs"
CAMPUS_UNION_FILE_PATH = "website/unions"
CAMPUS_KEY_OFFICIAL_FILE_PATH = "website/key-officials"


class SocialMediaPlatforms(BaseEnum):
    FACEBOOK = "FACEBOOK"
    TWITTER = "TWITTER"
    INSTAGRAM = "INSTAGRAM"
    LINKEDIN = "LINKEDIN"
    YOUTUBE = "YOUTUBE"
    GITHUB = "GITHUB"
    WEBSITE = "WEBSITE"
    OTHER = "OTHER"


class AcademicProgramTypes(BaseEnum):
    BACHELORS = "BACHELORS"
    MASTERS = "MASTERS"


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

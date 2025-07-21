from src.base.constants import BaseEnum

DEPARTMENT_THUMBNAIL_PATH = "department/thumbnails"
DEPARTMENT_PROGRAM_THUMBNAIL_PATH = "department/programs"
DEPARTMENT_STAFF_PHOTO_PATH = "department/staffs"
DEPARTMENT_DOWNLOADS_FILE_PATH = "department/downloads"
DEPARTMENT_EVENT_FILE_PATH = "department/events"


class DepartmentDesignationChoices(BaseEnum):
    HOD = "HOD"
    DHOD = "DHOD"
    STAFF = "STAFF"


class DepartmentEventTypes(BaseEnum):
    CULTURAL = "CULTURAL"
    TECHNICAL = "TECHNICAL"
    MUSICAL = "MUSICAL"
    SPORTS = "SPORTS"
    OTHER = "OTHER"

from src.base.constants import BaseEnum


class EmailTypes(BaseEnum):
    INFO = "INFO"
    HELP = "HELP"
    NOREPLY = "NOREPLY"


class StaffMemberTitle(BaseEnum):
    ER = "ER"
    PROF = "PROF"
    DR = "DR"
    MR = "MR"
    MRS = "MRS"
    MS = "MS"
    ASSOC_PROF = "ASSOC_PROF"
    ASST_PROF = "ASST_PROF"
    LECTURER = "LECTURER"
    TECHNICIAN = "TECHNICIAN"
    OTHER = "OTHER"


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

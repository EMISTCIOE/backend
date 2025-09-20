from src.base.constants import BaseEnum

PROJECT_MEDIA_PATH = "project/files"
PROJECT_MEMBER_IMAGE_PATH = "project/members"


class ProjectStatus(BaseEnum):
    PENDING = "PENDING"
    DRAFT = "DRAFT"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"


class LevelChoice(BaseEnum):
    MASTERS = "MASTERS"
    BACHELORS = "BACHELORS"
    PHD = "PHD"

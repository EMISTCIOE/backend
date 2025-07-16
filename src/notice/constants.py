from src.base.constants import BaseEnum


NOTICE_MEDIA_PATH = "notice/files"
NOTICE_THUMBNAIL_PATH = "notice/thumbnails"


class NoticeStatus(BaseEnum):
    PENDING = "PENDING"
    DRAFT = "DRAFT"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"


class MediaType(BaseEnum):
    IMAGE = "IMAGE"
    DOCUMENT = "DOCUMENT"

from django.utils.translation import gettext_lazy as _

# Errors msg
NOTICE_ALREADY_EXISTS = _("Notice already exists.")
MEDIA_NOT_FOUND = _("File not found.")

# Success Msg
NOTICE_CREATE_SUCCESS = _("Notice created successfully.")
NOTICE_UPDATE_SUCCESS = _("Notice updated successfully.")
NOTICE_DELETED_SUCCESS = _("Notice deleted successfully.")
MEDIA_DELETED_SUCCESS = _("File deleted successfully.")

TITLE_OR_MEDIA_REQUIRED = _(
    "A notice must have either a title or at least one media file."
)

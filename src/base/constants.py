from enum import Enum

from django.utils.translation import gettext_lazy as _


class BaseEnum(Enum):
    @classmethod
    def choices(cls):
        # Returns choices as (value, human-readable name)
        return [(key.value, _(key.name.replace("_", " ").title())) for key in cls]


PUBLIC_USER_ROLE = "PUBLIC-USER"  # Website User Base Role

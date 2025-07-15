from uuid import uuid4

from django.conf import settings
from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import AbstractUser

# Django Imports
from django.db import models
from django.utils.translation import gettext_lazy as _
from rest_framework_simplejwt.tokens import RefreshToken

# Project Imports
from src.base.models import AuditInfoModel

from src.base.constants import PUBLIC_USER_ROLE
from .exceptions import RoleNotFound
from .validators import validate_user_image


class UserRole(AuditInfoModel):
    """
    Role are a generic way of categorizing users to apply permissions, or
    some other label, to those users. A user can belong to any number of
    roles.
    """

    name = models.CharField(_("name"), max_length=50, unique=True)
    codename = models.CharField(_("codename"), max_length=50, unique=True)
    is_cms_role = models.BooleanField(
        _("Is CMS Role"),
        default=False,
        help_text=_("Is this role for CMS Users"),
    )

    class Meta:
        verbose_name = _("user role")
        verbose_name_plural = _("user roles")

    def __str__(self):
        return self.name


class UserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, username, email, password, **extra_fields):
        """
        Create and save a user with the given username, email, and password.
        """
        if not username:
            error_message = _("The given username must be set")
            raise ValueError(error_message)

        if email:
            email = self.normalize_email(email)

        user = self.model(username=username, email=email, **extra_fields)
        user.password = make_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, username, email=None, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(username, email, password, **extra_fields)

    def create_superuser(self, username, email=None, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            error_message = _("Superuser must have is_staff=True.")
            raise ValueError(error_message)
        if extra_fields.get("is_superuser") is not True:
            error_message = _("Superuser must have is_superuser=True.")
            raise ValueError(error_message)

        return self._create_user(username, email, password, **extra_fields)

    def create_system_user(
        self,
        username,
        email,
        password,
        context=None,
        **extra_fields,
    ):
        user: User = self.create_user(username, email, password, **extra_fields)
        return user

    def create_public_user(
        self,
        username,
        email,
        password,
        context=None,
        **extra_fields,
    ):
        user: User = self.create_user(username, email, password, **extra_fields)

        try:
            role = UserRole.objects.get(codename=PUBLIC_USER_ROLE)
            user.roles.add(role)
            user.save()
        except UserRole.DoesNotExist as err:
            role = "Public User"
            raise RoleNotFound(role) from err
        return user


class User(AbstractUser):
    """
    User Model

    This model represents a user in the system,
    extending the abstract user functionality provided by Django's
    """

    uuid = models.UUIDField(default=uuid4, unique=True, editable=False)

    phone_no = models.CharField(_("phone number"), max_length=15, blank=True)
    photo = models.ImageField(
        validators=[validate_user_image],
        blank=True,
        null=True,
        default="",
    )
    is_archived = models.BooleanField(
        _("archived"),
        default=False,
        help_text=_(
            "Designates whether this user should be treated as delected. "
            "Unselect this instead of deleting users.",
        ),
    )
    roles = models.ManyToManyField(
        UserRole,
        blank=True,
        verbose_name=_("roles"),
        help_text=_("Specific roles for this user"),
    )
    is_email_verified = models.BooleanField(default=False)
    is_phone_verified = models.BooleanField(default=False)
    updated_at = models.DateTimeField(_("date updated"), auto_now=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        null=True,
    )
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        on_delete=models.PROTECT,
        related_name="editor_user",
    )

    objects = UserManager()

    EMAIL_FIELD = "email"
    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = ["email"]

    class Meta:
        ordering = ["-id"]
        verbose_name = _("user")
        verbose_name_plural = _("users")
        constraints = [
            models.UniqueConstraint(
                fields=["email"],
                condition=models.Q(is_archived=False),
                name="unique_email_active_user",
            ),
        ]

    def clean(self):
        super().clean()
        self.email = self.__class__.objects.normalize_email(self.email)

    def __str__(self):
        return str(self.email)

    def get_upload_path(self, upload_path, filename):
        return f"{upload_path}/{filename}"

    @property
    def tokens(self):
        refresh = RefreshToken.for_user(self)
        return {"refresh": str(refresh), "access": str(refresh.access_token)}


class UserAccountVerification(models.Model):
    """User Account Verification"""

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    token = models.CharField(max_length=256)
    created_at = models.DateTimeField()
    is_archived = models.BooleanField(default=False)

    class Meta:
        ordering = ["-id"]

    def __str__(self):
        return f"User Id: {self.user.id!s} + '-' + {self.token}"

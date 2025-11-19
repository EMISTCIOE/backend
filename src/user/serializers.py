# Django Imports
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers

# Project Imports
from src.base.serializers import AbstractInfoRetrieveSerializer
from src.department.models import Department
from src.libs.get_context import get_user_by_context
from src.user.constants import SYSTEM_USER_ROLE
from src.website.models import CampusStaffDesignation, CampusUnion, StudentClub

from .messages import (
    USER_CREATED,
    USER_ERRORS,
    USER_ROLE_CREATED,
    USER_ROLE_ERRORS,
    USER_ROLE_UPDATED,
    USER_UPDATED,
)
from .models import Permission, Role, User
from .utils import send_user_welcome_email
from .utils.generators import generate_strong_password
from .utils.generators import generate_role_codename, generate_unique_user_username
from .validators import validate_user_image

# User Role Serializers


class GetPermissionForRoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Permission
        fields = ["id", "name", "codename", "permission_category"]


class RoleListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = ["id", "name", "codename", "is_active", "created_at"]


class RoleRetrieveSerializer(AbstractInfoRetrieveSerializer):
    permissions = serializers.SerializerMethodField()

    class Meta(AbstractInfoRetrieveSerializer.Meta):
        model = Role
        fields = ["id", "name", "codename", "permissions"]

        fields += AbstractInfoRetrieveSerializer.Meta.fields

    def get_permissions(self, obj) -> list:
        permissions = obj.permissions.filter(is_active=True)
        serializer = GetPermissionForRoleSerializer(permissions, many=True)
        return serializer.data


class RoleCreateSerializer(serializers.ModelSerializer):
    permissions = serializers.ListField(
        child=serializers.PrimaryKeyRelatedField(
            queryset=Permission.objects.filter(is_active=True),
        ),
        allow_empty=True,
        required=False,
    )

    class Meta:
        model = Role
        fields = ["name", "permissions", "is_active"]

    def validate_name(self, name):
        name = name.title()

        if Role.objects.filter(name__iexact=name).exists():
            raise serializers.ValidationError(
                USER_ROLE_ERRORS["ROLE_NAME"].format(name=name),
            )
        return name

    def create(self, validated_data):
        created_by = get_user_by_context(self.context)
        # Get the permissions
        permissions = validated_data.pop("permissions", [])

        # Generate codename
        name = validated_data.get("name")
        codename = generate_role_codename(name)

        # Create Role instance
        role = Role.objects.create(
            name=name.title(),
            codename=codename,
            created_by=created_by,
        )
        role.permissions.set(permissions)
        role.save()
        return role

    def to_representation(self, instance):
        return {"id": instance.id, "message": USER_ROLE_CREATED}


class RolePatchSerializer(serializers.ModelSerializer):
    permissions = serializers.ListField(
        child=serializers.PrimaryKeyRelatedField(
            queryset=Permission.objects.filter(is_active=True, is_archived=False),
        ),
        allow_empty=True,
        required=False,
    )

    class Meta:
        model = Role
        fields = ["name", "permissions", "is_active"]

    def validate_name(self, name):
        name = name.title()

        if Role.objects.filter(name__iexact=name).exclude(pk=self.instance.id).exists():
            raise serializers.ValidationError(
                USER_ROLE_ERRORS["ROLE_NAME"].format(name=name),
            )

        return name

    def update(self, instance: Role, validated_data):
        current_user = get_user_by_context(self.context)
        name = validated_data.get("name")
        # Get the permissions
        permissions = validated_data.get("permissions")

        validated_data["codename"] = generate_role_codename(name)

        instance.name = validated_data.get("name").title()
        instance.codename = validated_data.get("codename")
        instance.is_active = validated_data.get("is_active")
        instance.updated_by = current_user
        instance.permissions.set(permissions)
        instance.save()

        return instance

    def to_representation(self, instance):
        return {"id": instance.id, "message": USER_ROLE_UPDATED}


# User Setup Serializers


class GetUserRolesForUserListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = ["id", "name", "codename"]


class UserListSerializer(serializers.ModelSerializer):
    created_by_username = serializers.CharField(source="created_by.username")
    designation_title = serializers.CharField(
        source="designation.title",
        read_only=True,
    )
    department_name = serializers.CharField(
        source="department.name",
        read_only=True,
    )
    club_name = serializers.CharField(
        source="club.name",
        read_only=True,
    )
    union_name = serializers.CharField(
        source="union.name",
        read_only=True,
    )
    role_display = serializers.CharField(
        source="get_role_display",
        read_only=True,
    )

    class Meta:
        model = User
        exclude = [
            "uuid",
            "password",
            "is_superuser",
            "is_staff",
            "user_permissions",
            "is_archived",
            "groups",
            "roles",
            "permissions",
        ]


class UserRetrieveSerializer(serializers.ModelSerializer):
    roles = serializers.SerializerMethodField()
    created_by_username = serializers.CharField(source="created_by.username")
    designation_title = serializers.CharField(
        source="designation.title",
        read_only=True,
    )
    department_name = serializers.CharField(
        source="department.name",
        read_only=True,
    )
    club_name = serializers.CharField(
        source="club.name",
        read_only=True,
    )
    union_name = serializers.CharField(
        source="union.name",
        read_only=True,
    )
    role_display = serializers.CharField(
        source="get_role_display",
        read_only=True,
    )

    class Meta:
        model = User
        exclude = [
            "uuid",
            "password",
            "is_superuser",
            "is_staff",
            "user_permissions",
            "is_archived",
            "groups",
        ]

    def get_roles(self, obj) -> list:
        """
        Return only active, non-archived, and non-system-managed roles.
        """
        roles = obj.roles.filter(is_active=True, is_system_managed=False)
        serializer = GetUserRolesForUserListSerializer(roles, many=True)
        return serializer.data


class UserRegisterSerializer(serializers.ModelSerializer):
    """User Register Serializer"""

    first_name = serializers.CharField(max_length=50, required=True)
    last_name = serializers.CharField(max_length=50, required=True)
    phone_no = serializers.CharField(max_length=15, required=False, allow_blank=True)
    email = serializers.EmailField(required=True)
    photo = serializers.ImageField(
        allow_null=True,
        required=False,
        validators=[validate_user_image],
    )
    roles = serializers.PrimaryKeyRelatedField(
        queryset=Role.objects.filter(is_active=True, is_system_managed=False),
        many=True,
    )
    username = serializers.CharField(allow_blank=True)
    # Password is optional when creating users from CMS; backend will generate a strong
    # password if not provided by frontend and will include it in the welcome email.
    password = serializers.CharField(validators=[validate_password], required=False, write_only=True)

    role = serializers.ChoiceField(
        choices=User.RoleType.choices,
        default=User.RoleType.EMIS_STAFF,
        write_only=True,
    )
    designation = serializers.PrimaryKeyRelatedField(
        queryset=CampusStaffDesignation.objects.filter(is_active=True),
        required=False,
        allow_null=True,
    )
    department = serializers.PrimaryKeyRelatedField(
        queryset=Department.objects.all(),
        required=False,
        allow_null=True,
    )
    club = serializers.PrimaryKeyRelatedField(
        queryset=StudentClub.objects.all(),
        required=False,
        allow_null=True,
    )
    union = serializers.PrimaryKeyRelatedField(
        queryset=CampusUnion.objects.all(),
        required=False,
        allow_null=True,
    )

    class Meta:
        model = User
        fields = [
            "first_name",
            "last_name",
            "username",
            "password",
            "email",
            "photo",
            "phone_no",
            "roles",
            "role",
            "designation",
            "department",
            "club",
            "union",
            "is_active",
        ]

    def validate(self, attrs):
        # Username may be omitted from frontend; when present ensure uniqueness
        if attrs.get("username"):
            if User.objects.filter(username=attrs["username"]).exists():
                raise serializers.ValidationError(
                    {"username": USER_ERRORS["USERNAME_EXISTS"]},
                )

        if User.objects.filter(email=attrs["email"]).exists():
            raise serializers.ValidationError({"email": USER_ERRORS["EMAIL_EXISTS"]})

        if attrs.get("phone_no"):
            if User.objects.filter(phone_no=attrs["phone_no"]).exists():
                raise serializers.ValidationError(
                    {"phone_no": USER_ERRORS["PHONE_EXISTS"]},
                )

        if attrs["roles"] is None or attrs["roles"] == "":
            raise serializers.ValidationError({"roles": USER_ERRORS["MISSING_ROLES"]})

        role = attrs.get("role")
        if role == User.RoleType.CLUB and not attrs.get("club"):
            raise serializers.ValidationError(
                {"club": "Student club account must be linked to a club."},
            )
        if role == User.RoleType.UNION and not attrs.get("union"):
            raise serializers.ValidationError(
                {"union": "Union account must be linked to a union."},
            )
        if role == User.RoleType.DEPARTMENT_ADMIN and not attrs.get("department"):
            raise serializers.ValidationError(
                {"department": "Department admin must be assigned to a department."},
            )

        return attrs

    def create(self, validated_data):
        email = validated_data["email"]
        photo = validated_data.get("photo")
        # Generate a secure password if frontend didn't provide one
        password = validated_data.get("password") or generate_strong_password()

        username = validated_data.get("username")
        roles = validated_data.pop("roles", [])

        if not username:
            username = generate_unique_user_username(
                user_type=SYSTEM_USER_ROLE,
                email=email,
            )

        created_by = self.context["request"].user

        user_instance = User.objects.create_system_user(
            first_name=validated_data["first_name"].title().strip(),
            last_name=validated_data["last_name"].title().strip(),
            phone_no=validated_data.get("phone_no"),
            password=password,
            email=email,
            username=username,
            created_by=created_by,
            context=self.context,
            role=validated_data.get("role", User.RoleType.EMIS_STAFF),
        )

        if photo is not None:
            upload_path = user_instance.get_upload_path(
                upload_path="user/photos",
                filename=photo.name,
            )
            user_instance.photo.save(upload_path, photo)

        user_instance.designation = validated_data.get("designation")
        user_instance.department = validated_data.get("department")
        user_instance.club = validated_data.get("club")
        user_instance.union = validated_data.get("union")

        user_instance.roles.add(*roles)  # Set the roles

        user_instance.save()

        request = self.context.get("request")
        if request:
            send_user_welcome_email(user_instance, password, request)

        return user_instance

    def to_representation(self, instance):
        return {"id": instance.id, "message": USER_CREATED}


class UserPatchSerializer(serializers.ModelSerializer):
    """User Update Serializer"""

    first_name = serializers.CharField(max_length=50, required=False)
    last_name = serializers.CharField(max_length=50, required=False)
    photo = serializers.ImageField(
        allow_null=True,
        required=False,
        validators=[validate_user_image],
    )
    phone_no = serializers.CharField(max_length=10, required=False, allow_blank=True)
    roles = serializers.PrimaryKeyRelatedField(
        queryset=Role.objects.filter(is_active=True, is_system_managed=False),
        many=True,
    )
    role = serializers.ChoiceField(
        choices=User.RoleType.choices,
        required=False,
    )
    designation = serializers.PrimaryKeyRelatedField(
        queryset=CampusStaffDesignation.objects.filter(is_active=True),
        required=False,
        allow_null=True,
    )
    department = serializers.PrimaryKeyRelatedField(
        queryset=Department.objects.all(),
        required=False,
        allow_null=True,
    )
    club = serializers.PrimaryKeyRelatedField(
        queryset=StudentClub.objects.all(),
        required=False,
        allow_null=True,
    )
    union = serializers.PrimaryKeyRelatedField(
        queryset=CampusUnion.objects.all(),
        required=False,
        allow_null=True,
    )

    class Meta:
        model = User
        fields = [
            "first_name",
            "last_name",
            "roles",
            "photo",
            "phone_no",
            "is_active",
            "role",
            "designation",
            "department",
            "club",
            "union",
        ]

    def validate(self, attrs):
        if attrs.get("phone_no"):
            if (
                User.objects.filter(phone_no=attrs["phone_no"])
                .exclude(pk=self.instance.pk)
                .exists()
            ):
                raise serializers.ValidationError(
                    {"phone_no": USER_ERRORS["PHONE_EXISTS"]},
                )

        return attrs

    def update(self, instance: User, validated_data):
        current_user = get_user_by_context(self.context)
        photo = validated_data.get("photo")

        first_name = validated_data.get("first_name")
        if first_name:
            instance.first_name = first_name.title()
        last_name = validated_data.get("last_name")
        if last_name:
            instance.last_name = last_name.title()
        if "is_active" in validated_data:
            instance.is_active = validated_data.get("is_active")

        if "phone_no" in validated_data:
            instance.phone_no = validated_data.get("phone_no")
        instance.updated_by = current_user

        if "photo" in validated_data:
            if photo is not None:
                upload_path = instance.get_upload_path(
                    upload_path="user/photos",
                    filename=photo.name,
                )
                instance.photo.delete(save=False)  # Remove the old file
                instance.photo.save(upload_path, photo)
            else:
                instance.photo.delete(
                    save=True,
                )  # Delete the existing photo if photo is None

        if "role" in validated_data:
            instance.role = validated_data.get("role")

        if "roles" in validated_data:
            system_roles = list(instance.roles.filter(is_system_managed=True))
            roles_val = validated_data.get("roles")
            instance.roles.set(roles_val)
            instance.roles.add(*system_roles)

        if "designation" in validated_data:
            instance.designation = validated_data.get("designation")
        if "department" in validated_data:
            instance.department = validated_data.get("department")
        if "club" in validated_data:
            instance.club = validated_data.get("club")
        if "union" in validated_data:
            instance.union = validated_data.get("union")

        instance.save()
        return instance

    def to_representation(self, instance):
        return {"id": instance.id, "message": USER_UPDATED}

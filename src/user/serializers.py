# Django Imports
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers

# Project Imports
from src.libs.get_context import get_user_by_context

from .messages import USER_CREATED, USER_ERRORS, USER_UPDATED
from .models import UserRole, User
from .utils.generators import generate_unique_user_username
from .validators import validate_user_image


# User Setup Serializers


class GetUserRolesForUserListSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserRole
        fields = ["id", "name", "codename"]


class UserListSerializer(serializers.ModelSerializer):
    created_by_username = serializers.CharField(source="created_by.username")

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
        ]


class UserRetrieveSerializer(serializers.ModelSerializer):
    roles = serializers.SerializerMethodField()
    created_by_username = serializers.CharField(source="created_by.username")

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
        roles = obj.roles.filter(is_active=True, is_cms_role=True)
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
        queryset=UserRole.objects.filter(is_active=True, is_cms_role=False),
        many=True,
    )
    username = serializers.CharField(allow_blank=True)
    password = serializers.CharField(validators=[validate_password])

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
            "is_active",
        ]

    def validate(self, attrs):
        if attrs["username"]:
            if User.objects.filter(username=attrs["username"]).exists():
                raise serializers.ValidationError(
                    {"username": USER_ERRORS["USERNAME_EXISTS"]},
                )

        if User.objects.filter(email=attrs["email"]).exists():
            raise serializers.ValidationError({"email": USER_ERRORS["EMAIL_EXISTS"]})

        if attrs["phone_no"]:
            if User.objects.filter(phone_no=attrs["phone_no"]).exists():
                raise serializers.ValidationError(
                    {"phone_no": USER_ERRORS["PHONE_EXISTS"]},
                )

        if attrs["roles"] is None or attrs["roles"] == "":
            raise serializers.ValidationError({"roles": USER_ERRORS["MISSING_ROLES"]})

        return attrs

    def create(self, validated_data):
        email = validated_data["email"]
        photo = validated_data.get("photo", None)

        username = validated_data.get("username", "")
        roles = validated_data.pop("roles", [])

        if not username:
            username = generate_unique_user_username(
                user_type="CMS",
                email=email,
            )

        created_by = self.context["request"].user

        user_instance = User.objects.create_system_user(
            first_name=validated_data["first_name"].title().strip(),
            last_name=validated_data["last_name"].title().strip(),
            phone_no=validated_data["phone_no"],
            password=validated_data["password"],
            email=email,
            username=username,
            created_by=created_by,
            context=self.context,
        )

        if photo is not None:
            upload_path = user_instance.get_upload_path(
                upload_path="user/photos",
                filename=photo.name,
            )
            user_instance.photo.save(upload_path, photo)

        user_instance.roles.add(*roles)  # Set the roles

        user_instance.save()

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
        queryset=UserRole.objects.filter(is_active=True, is_cms_role=True),
        many=True,
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
        ]

    def validate(self, attrs):
        if attrs["phone_no"]:
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
        photo = validated_data.get("photo", None)

        instance.first_name = validated_data.get(
            "first_name",
            instance.first_name,
        ).title()
        instance.last_name = validated_data.get("last_name", instance.last_name).title()
        instance.is_active = validated_data.get("is_active", instance.is_active)

        instance.phone_no = validated_data.get("phone_no", instance.phone_no)
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

        if "roles" in validated_data:
            roles = validated_data.get("roles", [])
            instance.roles.set(roles)

        instance.save()
        return instance

    def to_representation(self, instance):
        return {"id": instance.id, "message": USER_UPDATED}

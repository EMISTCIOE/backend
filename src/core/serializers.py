from typing import Any

from django.utils.translation import gettext as _
from rest_framework import serializers

from src.base.serializers import AbstractInfoRetrieveSerializer

from src.core.messages import (
    EMAIL_CONFIG_CREATE_SUCCESS,
    EMAIL_CONFIG_UPDATE_SUCCESS,
    EMAIL_TYPE_EXISTS,
)
from src.core.models import EmailConfig
from src.libs.get_context import get_user_by_context


class EmailConfigListSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmailConfig
        fields = [
            "id",
            "email_type",
            "default_from_email",
            "server_mail",
            "is_active",
        ]


class EmailConfigRetrieveSerializer(AbstractInfoRetrieveSerializer):
    class Meta(AbstractInfoRetrieveSerializer.Meta):
        model = EmailConfig
        custom_fields = [
            "id",
            "email_type",
            "email_host",
            "email_use_tls",
            "email_use_ssl",
            "email_port",
            "email_host_user",
            "email_host_password",
            "email_host_user",
            "default_from_email",
            "server_mail",
        ]

        fields = custom_fields + AbstractInfoRetrieveSerializer.Meta.fields


class EmailConfigCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmailConfig
        fields = [
            "email_type",
            "email_host_user",
            "email_host_password",
            "default_from_email",
            "server_mail",
            "is_active",
        ]

    def validate_email_type(self, value):
        if EmailConfig.objects.filter(email_type=value).exists():
            raise serializers.ValidationError(EMAIL_TYPE_EXISTS)

        return value

    def create(self, validated_data):
        created_by = get_user_by_context(self.context)
        validated_data["created_by"] = created_by

        return EmailConfig.objects.create(**validated_data)

    def to_representation(self, instance):
        return {"message": EMAIL_CONFIG_CREATE_SUCCESS, "id": instance.id}


class EmailConfigPatchSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmailConfig
        fields = [
            "email_type",
            "email_host_user",
            "email_host_password",
            "default_from_email",
            "server_mail",
            "is_active",
        ]

    def validate_email_type(self, value):
        if (
            EmailConfig.objects.filter(email_type=value)
            .exclude(pk=self.instance.id)
            .exists()
        ):
            raise serializers.ValidationError(EMAIL_TYPE_EXISTS)

        return value

    def update(self, instance, validated_data):

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()

        return instance

    def to_representation(self, instance):
        return {"message": EMAIL_CONFIG_UPDATE_SUCCESS, "id": instance.id}

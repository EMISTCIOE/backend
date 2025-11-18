from typing import Any

from django.utils.translation import gettext as _
from rest_framework import serializers

from src.base.serializers import AbstractInfoRetrieveSerializer
from src.core.messages import (
    EMAIL_CONFIG_CREATE_SUCCESS,
    EMAIL_CONFIG_UPDATE_SUCCESS,
    EMAIL_TYPE_EXISTS,
)
from src.core.models import DashboardStats, EmailConfig
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


class DashboardStatsSerializer(serializers.ModelSerializer):
    """
    Serializer for Dashboard Statistics.
    Returns all statistics including graph data in a structured format.
    """

    class Meta:
        model = DashboardStats
        fields = [
            "calculated_at",
            # User Stats
            "total_users",
            "active_users",
            "new_users_this_month",
            "users_by_role",
            # Department Stats
            "total_departments",
            "active_departments",
            # Notice Stats
            "total_notices",
            "active_notices",
            "draft_notices",
            "featured_notices",
            "notices_by_category",
            "recent_notices_count",
            # Project Stats
            "total_projects",
            "projects_by_status",
            "projects_by_type",
            "projects_by_department",
            "completed_projects_this_year",
            # Research Stats
            "total_research",
            "research_by_status",
            "research_by_type",
            "published_research_this_year",
            # Journal Stats
            "total_articles",
            "total_authors",
            "total_board_members",
            # Curriculum Stats
            "total_subjects",
            "total_routines",
            "total_suggestions",
            # Feedback Stats
            "total_feedback_submissions",
            "pending_feedback",
            # Pending/Action Items
            "pending_notices",
            "pending_research",
            "pending_events",
            "pending_projects",
            # Graph Data
            "notices_trend",
            "users_growth",
            "research_publications_trend",
            "events_trend",
            "projects_trend",
        ]

    def to_representation(self, instance):
        """
        Custom representation to organize data into logical groups
        """
        data = super().to_representation(instance)

        # Organize into structured response
        return {
            "calculated_at": data["calculated_at"],
            "user_statistics": {
                "total": data["total_users"],
                "active": data["active_users"],
                "new_this_month": data["new_users_this_month"],
                "by_role": data["users_by_role"],
            },
            "department_statistics": {
                "total": data["total_departments"],
                "active": data["active_departments"],
            },
            "notice_statistics": {
                "total": data["total_notices"],
                "active": data["active_notices"],
                "draft": data["draft_notices"],
                "featured": data["featured_notices"],
                "by_category": data["notices_by_category"],
                "recent_count": data["recent_notices_count"],
            },
            "project_statistics": {
                "total": data["total_projects"],
                "by_status": data["projects_by_status"],
                "by_type": data["projects_by_type"],
                "by_department": data["projects_by_department"],
                "completed_this_year": data["completed_projects_this_year"],
            },
            "research_statistics": {
                "total": data["total_research"],
                "by_status": data["research_by_status"],
                "by_type": data["research_by_type"],
                "published_this_year": data["published_research_this_year"],
            },
            "journal_statistics": {
                "total_articles": data["total_articles"],
                "total_authors": data["total_authors"],
                "total_board_members": data["total_board_members"],
            },
            "curriculum_statistics": {
                "total_subjects": data["total_subjects"],
                "total_routines": data["total_routines"],
                "total_suggestions": data["total_suggestions"],
            },
            "feedback_statistics": {
                "total_submissions": data["total_feedback_submissions"],
                "pending_feedback": data["pending_feedback"],
            },
            "pending_items": {
                "notices": data["pending_notices"],
                "research": data["pending_research"],
                "events": data["pending_events"],
                "projects": data["pending_projects"],
                "feedback": data["pending_feedback"],
            },
            "chart_data": {
                "notices_trend": data["notices_trend"],
                "users_growth": data["users_growth"],
                "research_publications_trend": data["research_publications_trend"],
                "events_trend": data["events_trend"],
                "projects_trend": data["projects_trend"],
            },
        }

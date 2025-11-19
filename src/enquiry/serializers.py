"""
Enquiry Serializers
"""

from django.utils import timezone
from rest_framework import serializers

from src.user.models import User

from .models import MeetingEnquiry


class MeetingEnquiryListSerializer(serializers.ModelSerializer):
    """List meeting enquiries"""

    requester_name = serializers.CharField()
    requested_admin_name = serializers.CharField(
        source="requested_admin.get_full_name",
        read_only=True,
    )
    requested_admin_role = serializers.SerializerMethodField()
    status_display = serializers.CharField(source="get_status_display", read_only=True)

    class Meta:
        model = MeetingEnquiry
        fields = [
            "id",
            "requester_name",
            "requester_email",
            "requested_admin",
            "requested_admin_name",
            "requested_admin_role",
            "subject",
            "status",
            "status_display",
            "preferred_date",
            "scheduled_date",
            "created_at",
        ]

    def get_requested_admin_role(self, obj):
        return obj.get_admin_role()


class MeetingEnquiryDetailSerializer(serializers.ModelSerializer):
    """Detailed meeting enquiry"""

    requested_admin_details = serializers.SerializerMethodField()
    responded_by_name = serializers.CharField(
        source="responded_by.get_full_name",
        read_only=True,
        allow_null=True,
    )

    class Meta:
        model = MeetingEnquiry
        fields = [
            "id",
            "requester_name",
            "requester_email",
            "requester_phone",
            "requester_student_id",
            "requested_admin",
            "requested_admin_details",
            "subject",
            "message",
            "preferred_date",
            "preferred_time",
            "status",
            "response_message",
            "responded_by",
            "responded_by_name",
            "responded_at",
            "scheduled_date",
            "scheduled_time",
            "meeting_location",
            "meeting_notes",
            "email_sent",
            "created_at",
        ]

    def get_requested_admin_details(self, obj):
        admin = obj.requested_admin
        return {
            "id": admin.id,
            "name": admin.get_full_name(),
            "email": admin.email,
            "role": obj.get_admin_role(),
        }


class MeetingEnquiryCreateSerializer(serializers.ModelSerializer):
    """Create meeting enquiry - public endpoint"""

    class Meta:
        model = MeetingEnquiry
        fields = [
            "requester_name",
            "requester_email",
            "requester_phone",
            "requester_student_id",
            "requested_admin",
            "subject",
            "message",
            "preferred_date",
            "preferred_time",
        ]

    def validate_requested_admin(self, value):
        """Ensure requested admin has an admin profile"""
        allowed_roles = {
            User.RoleType.ADMIN,
            User.RoleType.DEPARTMENT_ADMIN,
            User.RoleType.EMIS_STAFF,
        }
        if value.role not in allowed_roles:
            raise serializers.ValidationError(
                "Selected user is not an admin. Please select a valid admin.",
            )
        return value

    def create(self, validated_data):
        enquiry = MeetingEnquiry.objects.create(**validated_data)
        # TODO: Send email notification to admin
        return enquiry

    def to_representation(self, instance):
        return {
            "id": instance.id,
            "message": "Your meeting request has been submitted successfully. You will receive an email notification.",
        }


class MeetingEnquiryResponseSerializer(serializers.ModelSerializer):
    """Admin response to enquiry"""

    class Meta:
        model = MeetingEnquiry
        fields = [
            "status",
            "response_message",
            "scheduled_date",
            "scheduled_time",
            "meeting_location",
            "meeting_notes",
        ]

    def validate(self, attrs):
        if attrs.get("status") == "ACCEPTED":
            if not attrs.get("scheduled_date") or not attrs.get("scheduled_time"):
                raise serializers.ValidationError(
                    "Scheduled date and time are required when accepting a meeting request.",
                )
        return attrs

    def update(self, instance, validated_data):
        instance.status = validated_data.get("status", instance.status)
        instance.response_message = validated_data.get(
            "response_message",
            instance.response_message,
        )
        instance.scheduled_date = validated_data.get(
            "scheduled_date",
            instance.scheduled_date,
        )
        instance.scheduled_time = validated_data.get(
            "scheduled_time",
            instance.scheduled_time,
        )
        instance.meeting_location = validated_data.get(
            "meeting_location",
            instance.meeting_location,
        )
        instance.meeting_notes = validated_data.get(
            "meeting_notes",
            instance.meeting_notes,
        )

        # Set response metadata
        instance.responded_by = self.context["request"].user
        instance.responded_at = timezone.now()

        instance.save()

        # TODO: Send email notification to requester
        return instance

    def to_representation(self, instance):
        return {
            "id": instance.id,
            "message": f"Meeting request has been {instance.get_status_display().lower()}.",
        }


class AdminListSerializer(serializers.ModelSerializer):
    """List available admins for enquiry"""

    role = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ["id", "first_name", "last_name", "email", "role"]

    def get_role(self, obj):
        if obj.designation:
            return obj.designation.title
        return obj.get_role_display()

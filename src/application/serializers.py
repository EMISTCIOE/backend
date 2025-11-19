"""
Email Request Serializers
"""

from django.utils import timezone
from rest_framework import serializers

from .models import EmailRequest


class EmailRequestListSerializer(serializers.ModelSerializer):
    """List email requests"""

    requester_name = serializers.CharField()
    request_type_display = serializers.CharField(
        source="get_request_type_display",
        read_only=True,
    )
    status_display = serializers.CharField(source="get_status_display", read_only=True)

    class Meta:
        model = EmailRequest
        fields = [
            "id",
            "requester_name",
            "requester_email",
            "request_type",
            "request_type_display",
            "subject",
            "status",
            "status_display",
            "request_number",
            "requires_application",
            "created_at",
        ]


class EmailRequestDetailSerializer(serializers.ModelSerializer):
    """Detailed email request"""

    processed_by_name = serializers.CharField(
        source="processed_by.get_full_name",
        read_only=True,
        allow_null=True,
    )

    class Meta:
        model = EmailRequest
        fields = [
            "id",
            "user",
            "requester_name",
            "requester_email",
            "requester_phone",
            "requester_department",
            "request_type",
            "subject",
            "message",
            "requested_email",
            "requires_application",
            "application_document",
            "request_number",
            "status",
            "response_message",
            "processed_by",
            "processed_by_name",
            "processed_at",
            "created_email",
            "created_at",
        ]


class EmailRequestCreateSerializer(serializers.ModelSerializer):
    """Create email request"""

    class Meta:
        model = EmailRequest
        fields = [
            "requester_name",
            "requester_email",
            "requester_phone",
            "requester_department",
            "request_type",
            "subject",
            "message",
            "requested_email",
            "application_document",
        ]

    def validate(self, attrs):
        requester_email = attrs.get("requester_email")
        
        # Check if application is needed
        if EmailRequest.needs_application(email=requester_email):
            if not attrs.get("application_document"):
                raise serializers.ValidationError({
                    "application_document": "You have made 10 or more requests. Application document is required for additional requests."
                })
        
        return attrs

    def create(self, validated_data):
        # Set user if authenticated
        user = self.context["request"].user if self.context["request"].user.is_authenticated else None
        
        email_request = EmailRequest.objects.create(
            user=user,
            **validated_data
        )
        
        # TODO: Send email notification
        
        return email_request

    def to_representation(self, instance):
        return {
            "id": instance.id,
            "request_number": instance.request_number,
            "message": f"Your email request has been submitted successfully. This is request #{instance.request_number}.",
            "requires_application_next_time": instance.request_number >= 10,
        }


class EmailRequestResponseSerializer(serializers.ModelSerializer):
    """Admin response to email request"""

    class Meta:
        model = EmailRequest
        fields = [
            "status",
            "response_message",
            "created_email",
            "email_password",
        ]

    def validate(self, attrs):
        if attrs.get("status") == "APPROVED":
            if attrs.get("request_type") == "NEW_EMAIL" and not attrs.get("created_email"):
                raise serializers.ValidationError({
                    "created_email": "Email address is required when approving a new email request."
                })
        return attrs

    def update(self, instance, validated_data):
        instance.status = validated_data.get("status", instance.status)
        instance.response_message = validated_data.get("response_message", instance.response_message)
        instance.created_email = validated_data.get("created_email", instance.created_email)
        instance.email_password = validated_data.get("email_password", instance.email_password)
        
        instance.processed_by = self.context["request"].user
        instance.processed_at = timezone.now()
        instance.save()
        
        # TODO: Send email notification to requester
        
        return instance

    def to_representation(self, instance):
        return {
            "id": instance.id,
            "message": f"Email request has been {instance.get_status_display().lower()}.",
        }

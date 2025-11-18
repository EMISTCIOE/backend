from rest_framework import serializers

# Project Imports
from src.base.serializers import AbstractInfoRetrieveSerializer
from src.contact.models import ContactType, PhoneNumber
from src.department.models import Department


class PhoneNumberListSerializer(serializers.ModelSerializer):
    """Serializer for listing phone numbers"""

    contact_type_display = serializers.CharField(
        source="get_contact_type_display",
        read_only=True,
    )
    department_id = serializers.IntegerField(
        source="department.id",
        read_only=True,
        allow_null=True,
    )
    department_name = serializers.CharField(
        source="department.name",
        read_only=True,
        allow_null=True,
    )

    class Meta:
        model = PhoneNumber
        fields = [
            "id",
            "contact_type",
            "contact_type_display",
            "department",
            "department_id",
            "department_name",
            "name",
            "phone_number",
            "description",
            "display_order",
            "is_active",
        ]


class PhoneNumberRetrieveSerializer(AbstractInfoRetrieveSerializer):
    """Serializer for retrieving a single phone number"""

    contact_type_display = serializers.CharField(
        source="get_contact_type_display",
        read_only=True,
    )
    department_details = serializers.SerializerMethodField()

    class Meta:
        model = PhoneNumber
        fields = AbstractInfoRetrieveSerializer.Meta.fields + [
            "contact_type",
            "contact_type_display",
            "department",
            "department_details",
            "name",
            "phone_number",
            "description",
            "display_order",
        ]

    def get_department_details(self, obj):
        if obj.department:
            return {
                "id": obj.department.id,
                "name": obj.department.name,
                "short_name": obj.department.short_name,
            }
        return None


class PhoneNumberCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating phone numbers"""

    class Meta:
        model = PhoneNumber
        fields = [
            "contact_type",
            "department",
            "name",
            "phone_number",
            "description",
            "display_order",
        ]

    def validate(self, data):
        """Validate that department is provided for department type contacts"""
        contact_type = data.get("contact_type", ContactType.SECTION)
        department = data.get("department")

        if contact_type == ContactType.DEPARTMENT and not department:
            raise serializers.ValidationError(
                {"department": "Department is required for department type contacts"},
            )

        if contact_type != ContactType.DEPARTMENT and department:
            raise serializers.ValidationError(
                {
                    "department": "Department should only be set for department type contacts",
                },
            )

        return data

    def create(self, validated_data):
        return PhoneNumber.objects.create(**validated_data)


class PhoneNumberUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating phone numbers"""

    class Meta:
        model = PhoneNumber
        fields = [
            "contact_type",
            "department",
            "name",
            "phone_number",
            "description",
            "display_order",
            "is_active",
        ]

    def validate(self, data):
        """Validate that department is provided for department type contacts"""
        contact_type = data.get("contact_type", self.instance.contact_type)
        department = data.get("department", self.instance.department)

        if contact_type == ContactType.DEPARTMENT and not department:
            raise serializers.ValidationError(
                {"department": "Department is required for department type contacts"},
            )

        if contact_type != ContactType.DEPARTMENT and department:
            raise serializers.ValidationError(
                {
                    "department": "Department should only be set for department type contacts",
                },
            )

        return data

    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance


# Public serializer for frontend consumption (no admin fields, only active records with phone numbers)
class PhoneNumberPublicSerializer(serializers.ModelSerializer):
    """Public serializer for phone numbers - used by frontend"""

    contact_type_display = serializers.CharField(
        source="get_contact_type_display",
        read_only=True,
    )

    class Meta:
        model = PhoneNumber
        fields = [
            "id",
            "contact_type",
            "contact_type_display",
            "name",
            "phone_number",
            "description",
            "display_order",
        ]

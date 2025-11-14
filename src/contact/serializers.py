from rest_framework import serializers

# Project Imports
from src.base.serializers import AbstractInfoRetrieveSerializer
from src.contact.models import PhoneNumber


class PhoneNumberListSerializer(serializers.ModelSerializer):
    """Serializer for listing phone numbers"""
    
    class Meta:
        model = PhoneNumber
        fields = [
            "id", 
            "department_name", 
            "phone_number", 
            "description", 
            "display_order",
            "is_active"
        ]


class PhoneNumberRetrieveSerializer(AbstractInfoRetrieveSerializer):
    """Serializer for retrieving a single phone number"""
    
    class Meta:
        model = PhoneNumber
        fields = AbstractInfoRetrieveSerializer.Meta.fields + [
            "department_name", 
            "phone_number", 
            "description", 
            "display_order"
        ]


class PhoneNumberCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating phone numbers"""
    
    class Meta:
        model = PhoneNumber
        fields = [
            "department_name", 
            "phone_number", 
            "description", 
            "display_order"
        ]
    
    def create(self, validated_data):
        return PhoneNumber.objects.create(**validated_data)


class PhoneNumberUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating phone numbers"""
    
    class Meta:
        model = PhoneNumber
        fields = [
            "department_name", 
            "phone_number", 
            "description", 
            "display_order",
            "is_active"
        ]
    
    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance


# Public serializer for frontend consumption (no admin fields)
class PhoneNumberPublicSerializer(serializers.ModelSerializer):
    """Public serializer for phone numbers - used by frontend"""
    
    class Meta:
        model = PhoneNumber
        fields = [
            "id",
            "department_name", 
            "phone_number", 
            "description", 
            "display_order"
        ]
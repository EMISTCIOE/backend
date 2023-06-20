from rest_framework import serializers
from .models import Department, StaffMembers, Society, Designation
from home.serializer import SocialMediaSerializer
from home.models import SocialMedia


class DepartmentSerializer(serializers.ModelSerializer):
    # this is for serializing many to many field social_media
    social_media = serializers.PrimaryKeyRelatedField(queryset=SocialMedia.objects.all(), many=True)
    class Meta:
        model = Department
        fields = ['id', 'name', 'introduction', 'description', 'image', 'social_media' ]

class StaffMembersSerializer(serializers.ModelSerializer):
    # this is for serializing many to many field social_media
    social_media = serializers.PrimaryKeyRelatedField(queryset=SocialMedia.objects.all(), many=True)
    class Meta:
        model = StaffMembers
        fields = ['id', 'name', 'photo', 'phone_number', 'email', 'message',  'department_id', 'designation_id', 'started_at', 'ended_at']

class SocietySerializer(serializers.ModelSerializer):
    # this is for serializing many to many field social_media
    social_media = serializers.PrimaryKeyRelatedField(queryset=SocialMedia.objects.all(), many=True)
    class Meta:
        model = Society
        fields = ['id', 'name', 'description', 'phone_number', 'email',  'department_id', 'founded_at']
        
class DesignationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Designation
        fields = ['id', 'designation', 'started_at', 'ended_at']
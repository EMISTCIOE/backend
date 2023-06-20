from rest_framework import serializers
from .models import Department, StaffMember, Society, Designation
from home.serializer import DepartmentSocialMediaSerializer, StaffMemberSocialMediaSerializer, SocietySocialMediaSerializer
from home.models import DepartmentSocialMedia, StaffMemberSocialMedia, SocietySocialMedia


class DepartmentSerializer(serializers.ModelSerializer):
    # this is for serializing many to many field social_media
    social_media = DepartmentSocialMediaSerializer(many=True, read_only=True)
    class Meta:
        model = Department
        fields = ['id', 'name', 'introduction', 'description', 'image', 'social_media' ]

class StaffMemberSerializer(serializers.ModelSerializer):
    # this is for serializing many to many field social_media
    social_media = StaffMemberSocialMediaSerializer(many=True, read_only=True)
    class Meta:
        model = StaffMember
        fields = ['id', 'name', 'photo', 'phone_number', 'email', 'message',  'department_id', 'designation_id', 'started_at', 'ended_at']

class SocietySerializer(serializers.ModelSerializer):
    # this is for serializing many to many field social_media
    social_media = SocietySocialMediaSerializer(many=True, read_only=True)
    class Meta:
        model = Society
        fields = ['id', 'name', 'description', 'phone_number', 'email',  'department_id', 'founded_at']
        
class DesignationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Designation
        fields = ['id', 'designation', 'started_at', 'ended_at']
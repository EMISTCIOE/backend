from .models import HomePage, SocialMedia
from rest_framework import serializers
# from rest_framework.relations import PrimaryKeyRelatedField

class HomePageSerializer(serializers.ModelSerializer):
    class Meta:
        model = HomePage
        fields = '__all__'
    
# class DepartmentSocialMediaSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = DepartmentSocialMedia
#         fields = '__all__'

# class StaffMemberSocialMediaSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = StaffMemberSocialMedia
#         fields = '__all__'

# class SocietySocialMediaSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = SocietySocialMedia
#         fields = '__all__'


class SocialMediaSerializer(serializers.Serializer):
    class Meta:
        model = SocialMedia
        fields = '__all__'

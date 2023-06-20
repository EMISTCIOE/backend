from .models import Home, SocialMedia
from rest_framework import serializers
# from rest_framework.relations import PrimaryKeyRelatedField

class HomeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Home
        fields = '__all__'
    
class SocialMediaSerializer(serializers.ModelSerializer):
    class Meta:
        model = SocialMedia
        fields = '__all__'
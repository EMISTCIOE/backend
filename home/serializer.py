from .models import HomePage, SocialMedia, Resource, Unit, ImageGallery, Image
from rest_framework import serializers

# from rest_framework.relations import PrimaryKeyRelatedField


class HomePageSerializer(serializers.ModelSerializer):
    class Meta:
        model = HomePage
        fields = '__all__'


class SocialMediaSerializer(serializers.ModelSerializer):
    class Meta:
        model = SocialMedia
        # fields = ['name', 'facebook', 'instagram', 'twitter', 'linkedin', 'github', 'youtube', 'website']
        fields = '__all__'


class ResourceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Resource
        fields = '__all__'


class UnitSerializer(serializers.ModelSerializer):
    unit_social = SocialMediaSerializer(read_only=True)
    class Meta:
        model = Unit
        fields = '__all__'


class ImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Image
        fields = '__all__'


class ImageGallerySerializer(serializers.ModelSerializer):
    image = ImageSerializer(many=True, read_only="True")

    class Meta:
        model = ImageGallery
        fields = ['name', 'description', 'image']

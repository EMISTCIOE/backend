from rest_framework import serializers
from src.home.models import (
    HomePage,
    SocialMedia,
    Unit,
    Resource,
    ImageGallery,
    Image,
    Calendar,
    Report,
)

class HomePagePublicSerializer(serializers.ModelSerializer):
    class Meta:
        model = HomePage
        fields = [
            'uuid',
            'name',
            'slider_image1',
            'slider_image2',
            'slider_image3',
            'slider_image4',
            'description',
            'phone_one',
            'phone_two',
            'phone_three',
            'email',
            'video',
            'video_description',
            'created_at',
            'updated_at',
        ]

class SocialMediaPublicSerializer(serializers.ModelSerializer):
    class Meta:
        model = SocialMedia
        fields = [
            'uuid',
            'name',
            'facebook',
            'twitter',
            'instagram',
            'linkedin',
            'youtube',
            'github',
            'website',
            'created_at',
            'updated_at',
        ]

class UnitPublicSerializer(serializers.ModelSerializer):
    unit_social = SocialMediaPublicSerializer(source='social_media', read_only=True)
    
    class Meta:
        model = Unit
        fields = [
            'uuid',
            'name',
            'description',
            'image',
            'unit_social',
            'created_at',
            'updated_at',
        ]

class ResourcePublicSerializer(serializers.ModelSerializer):
    class Meta:
        model = Resource
        fields = [
            'uuid',
            'title',
            'description',
            'image',
            'file',
            'is_featured',
            'is_downloadable',
            'created_at',
            'updated_at',
        ]

class ImageGalleryPublicSerializer(serializers.ModelSerializer):
    # Include related images in the response
    images = serializers.SerializerMethodField()
    
    class Meta:
        model = ImageGallery
        fields = [
            'uuid',
            'name',
            'description',
            'images',
            'created_at',
            'updated_at',
        ]
    
    def get_images(self, obj):
        # Get only active images
        images = obj.image_set.filter(is_active=True)
        return ImagePublicSerializer(images, many=True).data

class ImagePublicSerializer(serializers.ModelSerializer):
    gallery_name = serializers.CharField(source='gallery.name', read_only=True)
    
    class Meta:
        model = Image
        fields = [
            'uuid',
            'gallery_name',
            'name',
            'image',
            'created_at',
            'updated_at',
        ]

class CalendarPublicSerializer(serializers.ModelSerializer):
    class Meta:
        model = Calendar
        fields = [
            'uuid',
            'title',
            'calendar_level',
            'calendar_pdf',
            'slug',
            'academic_year',
            'created_at',
            'updated_at',
        ]

class ReportPublicSerializer(serializers.ModelSerializer):
    type_name = serializers.CharField(source='type.title', read_only=True)
    
    class Meta:
        model = Report
        fields = [
            'uuid',
            'title',
            'slug',
            'file',
            'type_name',
            'created_at',
            'updated_at',
        ]

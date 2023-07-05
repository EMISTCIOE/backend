from rest_framework import serializers

from .models import Notice, NoticeType, NoticeCategory



class NoticeTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = NoticeType
        fields = ['notice_type']

class NoticeCategorySerializer(serializers.ModelSerializer):
    notice_type = serializers.CharField(source='notice_type.notice_type', read_only=True)
    class Meta:
        model = NoticeCategory
        fields = ['notice_type', 'notice_category']


class NoticeSerializer(serializers.ModelSerializer):
    notice_category = NoticeCategorySerializer()
    class Meta:
        model = Notice
        depth = 1
        fields = ['id', 'slug', 'title', 'description', 'thumbnail', 'download_file', 'notice_category', 'department_id', 'is_featured', 'published_date', 'modified', 'is_active']


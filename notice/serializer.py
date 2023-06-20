from rest_framework.serializers import ModelSerializer

from .models import Notice, NoticeType, NoticeCategory

class NoticeSerializer(ModelSerializer):
    class Meta:
        model = Notice
        fields = '__all__'


class NoticeTypeSerializer(ModelSerializer):
    class Meta:
        model = NoticeType
        fields = '__all__'

class NoticeCategorySerializer(ModelSerializer):
    class Meta:
        model = NoticeCategory
        fields = ['notice_type', 'notice_category']
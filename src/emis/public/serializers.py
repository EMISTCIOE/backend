from rest_framework import serializers

from src.emis.models import EMISDownload, EMISNotice


class PublicEMISDownloadSerializer(serializers.ModelSerializer):
    class Meta:
        model = EMISDownload
        fields = ["uuid", "title", "description", "category", "file", "link_url", "created_at"]


class PublicEMISNoticeSerializer(serializers.ModelSerializer):
    class Meta:
        model = EMISNotice
        fields = [
            "uuid",
            "slug",
            "title",
            "summary",
            "body",
            "category",
            "severity",
            "published_at",
            "attachment",
            "external_url",
            "views",
        ]

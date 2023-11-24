from rest_framework import serializers
from .models import Subject, Routine


class SubjectSerializer(serializers.ModelSerializer):


    class Meta:
        model = Subject
        fields = [
            "id",
            "name",
            "slug",
            "semester",
            "code",
            "topics_covered",
        ]


class RoutineSerializer(serializers.ModelSerializer):
    class Meta:
        model = Routine
        fields = "__all__"

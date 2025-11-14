from rest_framework import serializers

from src.department.models import AcademicProgram

from .models import Routine, Subject, Suggestion


class AcademicProgramLiteSerializer(serializers.ModelSerializer):
    class Meta:
        model = AcademicProgram
        fields = ["uuid", "name", "short_name", "slug"]


class SubjectSerializer(serializers.ModelSerializer):
    academic_program = AcademicProgramLiteSerializer(read_only=True)

    class Meta:
        model = Subject
        fields = ["id", "name", "slug", "semester", "code", "topics_covered", "academic_program"]


class RoutineSerializer(serializers.ModelSerializer):
    class Meta:
        model = Routine
        fields = "__all__"


class SuggestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Suggestion
        fields = "__all__"

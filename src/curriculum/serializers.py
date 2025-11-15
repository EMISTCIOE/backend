from rest_framework import serializers

from src.department.models import AcademicProgram

from .models import Routine, Subject, Suggestion


class AcademicProgramLiteSerializer(serializers.ModelSerializer):
    class Meta:
        model = AcademicProgram
        fields = ["id", "uuid", "name", "short_name", "slug"]


class SubjectSerializer(serializers.ModelSerializer):
    academic_program = AcademicProgramLiteSerializer(read_only=True)
    academic_program_id = serializers.PrimaryKeyRelatedField(
        source='academic_program',
        queryset=AcademicProgram.objects.filter(is_active=True),
        required=False,
        allow_null=True,
        write_only=True
    )

    class Meta:
        model = Subject
        fields = [
            "id",
            "name",
            "slug",
            "semester",
            "code",
            "program",
            "topics_covered",
            "academic_program",
            "academic_program_id",
        ]


class RoutineSerializer(serializers.ModelSerializer):
    class Meta:
        model = Routine
        fields = "__all__"


class SuggestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Suggestion
        fields = "__all__"

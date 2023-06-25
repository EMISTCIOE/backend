from rest_framework import serializers
from .models import *


class DepartmentInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = DepartmentInfo
        fields = '__all__'


class SocialSerializer(serializers.ModelSerializer):
    class Meta:
        model = Social
        fields = '__all__'


class NoticeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notice
        fields = '__all__'


class NoticeTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = NoticeType
        fields = '__all__'


class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = '__all__'


class QuestionBankSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuestionBank
        fields = '__all__'


class ImageGallerySerializer(serializers.ModelSerializer):
    class Meta:
        model = ImageGallery
        fields = '__all__'


class PlansPolicySerializer(serializers.ModelSerializer):
    class Meta:
        model = PlansPolicy
        fields = '__all__'


class StudentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Student
        fields = '__all__'


class FAQSerializer(serializers.ModelSerializer):
    class Meta:
        model = FAQ
        fields = '__all__'


class BlogSerializer(serializers.ModelSerializer):
    class Meta:
        model = Blog
        fields = '__all__'


class ProgramsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Programs
        fields = '__all__'


class SemesterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Semester
        fields = '__all__'


class SubjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subject
        fields = '__all__'


class DepartmentLoginSerializer(serializers.ModelSerializer):
    social = SocialSerializer()
    plans = serializers.PrimaryKeyRelatedField(
        queryset=PlansPolicy.objects.all())

    class Meta:
        model = DepartmentLogin
        fields = '__all__'

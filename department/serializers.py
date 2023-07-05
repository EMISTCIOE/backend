from rest_framework import serializers
from .models import Department, Project, QuestionBank, PlansPolicy, Student, FAQ, Blog, Programs, Semester, Subject, StaffMember, Designation, Society, Routine
from home.serializer import SocialMediaSerializer


class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        depth = 1
        fields = ['id', 'name', 'slug', 'description',
                  'report', 'published_link', 'department']


class QuestionBankSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuestionBank
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


class SubjectSerializer(serializers.ModelSerializer):
    semester = serializers.CharField(source='semester.name')

    class Meta:
        model = Subject
        fields = ['id', 'name', 'slug', 'semester',
                  'code', 'course_objective', 'topics_covered']


class SemesterSerializer(serializers.ModelSerializer):
    subjects = SubjectSerializer(many=True, read_only=True)

    class Meta:
        model = Semester
        depth = 1
        fields = ['id', 'name', 'slug', 'subjects']


class ProgramsSerializer(serializers.ModelSerializer):
    semesters = SemesterSerializer(many=True, read_only=True)
    department = serializers.CharField(source='department.name')

    class Meta:
        model = Programs
        depth = 1
        fields = ['id', 'slug', 'name',
                  'description', 'department', 'semesters']


class StaffMemberSerializer(serializers.ModelSerializer):
    staff_designation = serializers.CharField(
        source='designation_id.designation')
    department = serializers.CharField(source='department_id.name')
    socials = SocialMediaSerializer(many=True, read_only=True)

    class Meta:
        model = StaffMember
        depth = 1
        fields = ['id', 'slug', 'name', 'staff_designation', 'is_key_official', 'responsibility',
                  'photo', 'socials', 'phone_number', 'email', 'department', 'message']


class DesignationSerializer(serializers.ModelSerializer):
    associated_person = StaffMemberSerializer(many=True, read_only=True)

    class Meta:
        model = Designation
        depth = 1
        fields = ['id', 'designation', 'associated_person']


class SocietySerializer(serializers.ModelSerializer):
    class Meta:
        model = Society
        fields = '__all__'


class RoutineSerializer(serializers.ModelSerializer):
    class Meta:
        model = Routine
        fields = '__all__'


class DepartmentSerializer(serializers.ModelSerializer):
    staff_members = StaffMemberSerializer(many=True, read_only=True)
    department_programs = ProgramsSerializer(many=True, read_only=True)
    department_projects = ProjectSerializer(many=True, read_only=True)

    class Meta:
        model = Department
        depth = 1
        fields = ['id', 'slug', 'name', 'introduction', 'description', 'profile', 'social_media', 'phone',
                  'email', 'routine', 'plans', 'profile', 'is_academic', 'department_programs', 'staff_members', "department_projects"]

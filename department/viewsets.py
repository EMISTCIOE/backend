from rest_framework import viewsets
from .models import Department, Project, QuestionBank, PlansPolicy, Student, FAQ, Blog, Programs, Semester, Subject, StaffMember, Designation, Society, Routine
from .serializers import DepartmentSerializer, ProjectSerializer, QuestionBankSerializer, PlansPolicySerializer, StudentSerializer, FAQSerializer, BlogSerializer, ProgramsSerializer, SemesterSerializer, SubjectSerializer, StaffMemberSerializer, DesignationSerializer, SocietySerializer, RoutineSerializer
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated


class DepartmentViewSet(viewsets.ModelViewSet):
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer
    permission_classes = [IsAuthenticated]


class ProjectViewSet(viewsets.ModelViewSet):
    queryset = Project.objects.all().order_by('-created_at')
    paginate_by = 10
    serializer_class = ProjectSerializer
    permission_classes = [IsAuthenticated]


class QuestionBankViewSet(viewsets.ModelViewSet):
    queryset = QuestionBank.objects.all()
    serializer_class = QuestionBankSerializer
    permission_classes = [IsAuthenticated]


class PlansPolicyViewSet(viewsets.ModelViewSet):
    queryset = PlansPolicy.objects.all()
    serializer_class = PlansPolicySerializer
    permission_classes = [IsAuthenticated]


class StudentViewSet(viewsets.ModelViewSet):
    queryset = Student.objects.all()
    serializer_class = StudentSerializer
    permission_classes = [IsAuthenticated]


class FAQViewSet(viewsets.ModelViewSet):
    queryset = FAQ.objects.all()
    serializer_class = FAQSerializer
    permission_classes = [IsAuthenticated]


class BlogViewSet(viewsets.ModelViewSet):
    queryset = Blog.objects.all()
    serializer_class = BlogSerializer
    permission_classes = [IsAuthenticated]


class ProgramsViewSet(viewsets.ModelViewSet):
    queryset = Programs.objects.all()
    serializer_class = ProgramsSerializer
    permission_classes = [IsAuthenticated]


class SemesterViewSet(viewsets.ModelViewSet):
    queryset = Semester.objects.all()
    serializer_class = SemesterSerializer
    permission_classes = [IsAuthenticated]


class SubjectViewSet(viewsets.ModelViewSet):
    queryset = Subject.objects.all()
    serializer_class = SubjectSerializer
    permission_classes = [IsAuthenticated]


class StaffMemberViewSet(viewsets.ModelViewSet):
    queryset = StaffMember.objects.all()
    serializer_class = StaffMemberSerializer
    # permission_classes = [IsAuthenticated]


class DesignationViewSet(viewsets.ModelViewSet):
    queryset = Designation.objects.all()
    serializer_class = DesignationSerializer
    permission_classes = [IsAuthenticated]


class SocietyViewSet(viewsets.ModelViewSet):
    queryset = Society.objects.all()
    serializer_class = SocietySerializer
    permission_classes = [IsAuthenticated]


class RoutineViewSet(viewsets.ModelViewSet):
    queryset = Routine.objects.all()
    serializer_class = RoutineSerializer
    permission_classes = [IsAuthenticated]

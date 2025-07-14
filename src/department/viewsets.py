from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticatedOrReadOnly

from .models import (
    FAQ,
    Blog,
    Department,
    Designation,
    PlansPolicy,
    Programs,
    Project,
    QuestionBank,
    Society,
    StaffMember,
    Student,
)
from .serializers import (
    BlogSerializer,
    DepartmentSerializer,
    DesignationSerializer,
    FAQSerializer,
    PlansPolicySerializer,
    ProgramsSerializer,
    ProjectSerializer,
    QuestionBankSerializer,
    SocietySerializer,
    StaffMemberSerializer,
    StudentSerializer,
)


class DepartmentViewSet(viewsets.ModelViewSet):
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]


class ProjectViewSet(viewsets.ModelViewSet):
    queryset = Project.objects.all().order_by("-created_at")
    paginate_by = 10
    serializer_class = ProjectSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]


class QuestionBankViewSet(viewsets.ModelViewSet):
    queryset = QuestionBank.objects.all()
    serializer_class = QuestionBankSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]


class PlansPolicyViewSet(viewsets.ModelViewSet):
    queryset = PlansPolicy.objects.all()
    serializer_class = PlansPolicySerializer
    permission_classes = [IsAuthenticatedOrReadOnly]


class StudentViewSet(viewsets.ModelViewSet):
    queryset = Student.objects.all()
    serializer_class = StudentSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]


class FAQViewSet(viewsets.ModelViewSet):
    queryset = FAQ.objects.all()
    serializer_class = FAQSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]


class BlogViewSet(viewsets.ModelViewSet):
    queryset = Blog.objects.all()
    serializer_class = BlogSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]


class ProgramsViewSet(viewsets.ModelViewSet):
    queryset = Programs.objects.all()
    serializer_class = ProgramsSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]


class StaffMemberViewSet(viewsets.ModelViewSet):
    queryset = StaffMember.objects.all()
    serializer_class = StaffMemberSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]


class DesignationViewSet(viewsets.ModelViewSet):
    queryset = Designation.objects.all()
    serializer_class = DesignationSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]


class SocietyViewSet(viewsets.ModelViewSet):
    queryset = Society.objects.all()
    serializer_class = SocietySerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

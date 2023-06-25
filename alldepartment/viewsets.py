from rest_framework.viewsets import ModelViewSet
from .models import *
from .serealizers import *


class DepartmentViewSet(ModelViewSet):
    queryset = DepartmentInfo.objects.all()
    serializer_class = DepartmentInfoSerializer


class NoticeViewSet(ModelViewSet):
    queryset = Notice.objects.all()
    serializer_class = NoticeSerializer


class ProjectViewSet(ModelViewSet):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer


class StudentViewSet(ModelViewSet):
    queryset = Student.objects.all()
    serializer_class = StudentSerializer


class BlogViewSet(ModelViewSet):
    queryset = Blog.objects.all()
    serializer_class = BlogSerializer


class PorgramsViewSet(ModelViewSet):
    queryset = Programs.objects.all()
    serializer_class = ProgramsSerializer


class SubjectViewSet(ModelViewSet):
    queryset = Subject.objects.all()
    serializer_class = SubjectSerializer

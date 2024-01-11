from django.shortcuts import render
from .serializers import SubjectSerializer
from .models import Subject
from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticatedOrReadOnly


# Create your views here.
class DepartmentSubjects(ListAPIView):
    model = Subject
    serializer_class = SubjectSerializer
    paginate_by = 10
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        program = self.request.GET.get("program", "").lower()
        code = self.request.GET.get("code", "").lower()
        sub_name = self.request.GET.get("name", "").lower()
        queryset = Subject.objects.all()
        if department:
            queryset = queryset.filter(
                program__icontains=program)
        if code:
            queryset = queryset.filter(code__iexact=code)
        if sub_name:
            queryset = queryset.filter(name__icontains=sub_name)
        return queryset

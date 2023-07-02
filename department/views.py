from django.shortcuts import render
from .models import Subject
from rest_framework.generics import ListAPIView
from django.db.models import Q
from .serializers import SubjectSerializer


class DepartmentSubjects(ListAPIView):
    model = Subject
    serializer_class = SubjectSerializer
    paginate_by = 10

    def get_queryset(self):
        query = self.request.GET.get('faculty', '')
        queryset = Subject.objects.all()
        if query:
            queryset = Subject.objects.filter(semester__program__name__iexact = query)
        return queryset

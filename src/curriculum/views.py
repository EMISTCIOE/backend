from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view
from rest_framework.generics import ListAPIView
from rest_framework.parsers import JSONParser
from rest_framework.permissions import AllowAny, IsAuthenticatedOrReadOnly
from rest_framework.filters import OrderingFilter

from src.department.models import Department

from .models import Subject
from .serializers import SubjectSerializer, SuggestionSerializer


class DepartmentSubjects(ListAPIView):
    serializer_class = SubjectSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [OrderingFilter]
    ordering = ['code']

    def get_queryset(self):
        program_filter = self.request.GET.get('program', '')
        code = self.request.GET.get('code', '')
        sub_name = self.request.GET.get('name', '')
        queryset = Subject.objects.all()

        if program_filter:
            queryset = queryset.filter(
                Q(academic_program__slug__iexact=program_filter)
                | Q(program__icontains=program_filter)
            )
        if code:
            queryset = queryset.filter(code__iexact=code)
        if sub_name:
            queryset = queryset.filter(name__icontains=sub_name)
        return queryset


class DepartmentProgramSubjects(ListAPIView):
    serializer_class = SubjectSerializer
    permission_classes = [AllowAny]
    filter_backends = [OrderingFilter]
    ordering = ['semester', 'code']

    def get_queryset(self):
        department = get_object_or_404(
            Department,
            slug=self.kwargs['slug'],
            is_active=True,
            is_archived=False,
        )
        program_slug = self.request.GET.get('program')
        queryset = Subject.objects.filter(
            Q(academic_program__department=department)
            | Q(
                academic_program__isnull=True,
                program__in=department.department_programs.values_list('name', flat=True)
            )
        )

        if program_slug:
            program = department.department_programs.filter(slug=program_slug).first()
            if program:
                queryset = queryset.filter(
                    Q(academic_program=program)
                    | Q(
                        academic_program__isnull=True,
                        program__iexact=program.name,
                    )
                )
            else:
                queryset = queryset.filter(program__icontains=program_slug.replace('-', ' '))
        return queryset


# Custom view for suggestion submissions
@api_view(['POST'])
def suggestion_create_view(request):
    if request.method == 'POST':
        data = JSONParser().parse(request)
        serializer = SuggestionSerializer(data=data)

        if serializer.is_valid():
            serializer.save()
            return JsonResponse(serializer.data, status=201)
        return JsonResponse(serializer.errors, status=400)

    return JsonResponse({ 'error': 'Only POST requests are allowed' }, status=405)

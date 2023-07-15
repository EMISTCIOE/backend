from django.shortcuts import render
from .models import Subject, StaffMember, Department, Blog, QuestionBank
from rest_framework.generics import ListAPIView
from django.db.models import Q
from .serializers import SubjectSerializer, StaffMemberSerializer, BlogSerializer, QuestionBankSerializer
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated


# Search view to search subject using faculty, department, code and subject name


class DepartmentSubjects(ListAPIView):
    model = Subject
    serializer_class = SubjectSerializer
    paginate_by = 10
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        print(self.request.GET)
        faculty = self.request.GET.get('faculty', '').lower()
        department = self.request.GET.get('department', '').lower()
        code = self.request.GET.get('code', '').lower()
        sub_name = self.request.GET.get('name', '').lower()
        queryset = Subject.objects.all()
        if faculty:
            queryset = queryset.filter(
                semester__program__faculty__name__icontains=faculty)
        if department:
            queryset = queryset.filter(
                semester__program__department__name__icontains=department)
        if code:
            queryset = queryset.filter(code__iexact=code)
        if sub_name:
            queryset = queryset.filter(name__icontains=sub_name)
        return queryset


class StaffSearchViews(ListAPIView):
    model = StaffMember
    serializer_class = StaffMemberSerializer
    paginate_by = 10

    def get_queryset(self):
        # search by designation and is_key_official
        name = self.request.GET.get('name', '').lower()
        designation = self.request.GET.get('designation', '').lower()
        key_officials = self.request.GET.get('key_officials', '').lower()
        department = self.request.GET.get('department', '').lower()
        queryset = StaffMember.objects.all()
        if designation:
            queryset = queryset.filter(
                designation_id__designation__icontains=designation)
        if key_officials:
            queryset = queryset.filter(
                is_key_official__iexact=key_officials)
        if name:
            queryset = queryset.filter(name__icontains=name)
        if department:
            queryset = queryset.filter(
                department_id__name__icontains=department)
        return queryset

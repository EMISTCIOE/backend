from django.db.models import Q
from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticatedOrReadOnly

from .models import StaffMember
from .serializers import StaffMemberSerializer

# Search view to search subject using faculty, department, code and subject name


class StaffSearchViews(ListAPIView):
    model = StaffMember
    serializer_class = StaffMemberSerializer
    paginate_by = 10
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        # search by designation and is_key_official
        name = self.request.GET.get("name", "").lower()
        rank = self.request.GET.get("rank", "").lower()
        key_officials = self.request.GET.get("key_officials", "").lower()
        department = self.request.GET.get("department", "").lower()
        queryset = StaffMember.objects.all()
        if rank:
            queryset = queryset.filter(designation_id__rank__iexact=rank)
        if key_officials:
            queryset = queryset.filter(is_key_official__iexact=key_officials)
        if name:
            queryset = queryset.filter(name__icontains=name)
        if department:
            queryset = queryset.filter(department_id__name__icontains=department)
        return queryset

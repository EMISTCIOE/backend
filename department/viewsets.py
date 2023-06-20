from rest_framework.viewsets import ModelViewSet
from .models import Department, Designation, StaffMembers, Society
from .serializer import DepartmentSerializer, DesignationSerializer, StaffMembersSerializer, SocietySerializer
from .forms import DepartmentForm

# Create your views here.
# using viewsets instead of apiviews as it will automatically generate urls for us and can be used for both list and detail views with multiple http reqquest methods
class DepartmentViewSet(ModelViewSet):
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer
    form_class = DepartmentForm


class DesignationViewSet(ModelViewSet):
    queryset = Designation.objects.all()
    serializer_class = DesignationSerializer

class StaffMembersViewSet(ModelViewSet):
    queryset = StaffMembers.objects.all()
    serializer_class = StaffMembersSerializer

class SocietyViewSet(ModelViewSet):
    queryset = Society.objects.all()
    serializer_class = SocietySerializer
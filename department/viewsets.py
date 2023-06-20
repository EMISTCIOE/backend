from rest_framework.viewsets import ModelViewSet
from .models import Department, Designation, StaffMember, Society
from .serializer import DepartmentSerializer, DesignationSerializer, StaffMemberSerializer, SocietySerializer
# from .forms import DepartmentForm

# Create your views here.
# using viewsets instead of apiviews as it will automatically generate urls for us and can be used for both list and detail views with multiple http reqquest methods
class DepartmentViewSet(ModelViewSet):
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer
    # form_class = DepartmentForm


class DesignationViewSet(ModelViewSet):
    queryset = Designation.objects.all()
    serializer_class = DesignationSerializer

class StaffMemberViewSet(ModelViewSet):
    queryset = StaffMember.objects.all()
    serializer_class = StaffMemberSerializer

class SocietyViewSet(ModelViewSet):
    queryset = Society.objects.all()
    serializer_class = SocietySerializer
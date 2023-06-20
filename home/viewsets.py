from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from .models import HomePage, DepartmentSocialMedia, StaffMemberSocialMedia, SocietySocialMedia
from .serializer import HomePageSerializer, DepartmentSocialMediaSerializer, StaffMemberSocialMediaSerializer, SocietySocialMediaSerializer
# Create your views here.

class HomeViewSet(ModelViewSet):
    queryset = HomePage.objects.all()
    serializer_class = HomePageSerializer

    def list(self, request):
        queryset = HomePage.objects.all()
        serializer = HomePageSerializer(queryset, many=True)
        return Response(serializer.data)

class DepartmentSocialMediaViewSet(ModelViewSet):
    queryset = DepartmentSocialMedia.objects.all()
    serializer_class = DepartmentSocialMediaSerializer


class StaffMemberSocialMediaViewSet(ModelViewSet):
    queryset = StaffMemberSocialMedia.objects.all()
    serializer_class = StaffMemberSocialMediaSerializer


class SocietySocialMediaViewSet(ModelViewSet):
    queryset = SocietySocialMedia.objects.all()
    serializer_class = SocietySocialMediaSerializer
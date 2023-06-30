from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from .models import HomePage, SocialMedia
from .serializer import HomePageSerializer, SocialMediaSerializer, ResourceSerializer, UnitSerializer
# Create your views here.

class HomeViewSet(ModelViewSet):
    queryset = HomePage.objects.all()
    serializer_class = HomePageSerializer

    def list(self, request):
        queryset = HomePage.objects.all()
        serializer = HomePageSerializer(queryset, many=True)
        return Response(serializer.data)
    
class SocialMediaViewSet(ModelViewSet):
    queryset = SocialMedia.objects.all()
    serializer_class = SocialMediaSerializer

class ResourceViewSet(ModelViewSet):
    queryset = SocialMedia.objects.all()
    serializer_class = ResourceSerializer

class UnitViewSet(ModelViewSet):
    queryset = SocialMedia.objects.all()
    serializer_class = UnitSerializer
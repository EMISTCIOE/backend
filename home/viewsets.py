from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from .models import Home, SocialMedia
from .serializer import HomeSerializer, SocialMediaSerializer
# Create your views here.

class HomeViewSet(ModelViewSet):
    queryset = Home.objects.all()
    serializer_class = HomeSerializer

    def list(self, request):
        queryset = Home.objects.all()
        serializer = HomeSerializer(queryset, many=True)
        return Response(serializer.data)

class SocialMediaViewSet(ModelViewSet):
    queryset = SocialMedia.objects.all()
    serializer_class = SocialMediaSerializer

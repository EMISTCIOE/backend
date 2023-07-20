from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from .models import HomePage, SocialMedia, Resource, Unit, ImageGallery, Image
from .serializer import HomePageSerializer, SocialMediaSerializer, ResourceSerializer, UnitSerializer, ImageGallerySerializer, ImageSerializer
# Create your views here.
from rest_framework.permissions import IsAuthenticatedOrReadOnly


class HomeViewSet(ModelViewSet):
    queryset = HomePage.objects.all()
    serializer_class = HomePageSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def list(self, request):
        queryset = HomePage.objects.all()
        serializer = HomePageSerializer(queryset, many=True)
        return Response(serializer.data)


class SocialMediaViewSet(ModelViewSet):
    queryset = SocialMedia.objects.all()
    serializer_class = SocialMediaSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]


class ResourceViewSet(ModelViewSet):
    queryset = Resource.objects.all()
    serializer_class = ResourceSerializer
    paginate_by = 10
    # permission_classes = [IsAuthenticated]


class UnitViewSet(ModelViewSet):
    queryset = Unit.objects.all()
    serializer_class = UnitSerializer
    paginate_by = 10
    permission_classes = [IsAuthenticatedOrReadOnly]


class ImageGalleryViewset(ModelViewSet):
    queryset = ImageGallery.objects.all()
    serializer_class = ImageGallerySerializer
    paginate_by = 10
    permission_classes = [IsAuthenticatedOrReadOnly]


class ImageViewset(ModelViewSet):
    queryset = Image.objects.all()
    serializer_class = ImageSerializer
    paginate_by = 10
    permission_classes = [IsAuthenticatedOrReadOnly]

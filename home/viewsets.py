from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from .models import HomePage, SocialMedia, Resource, Unit, ImageGallery, Image
from .serializer import HomePageSerializer, SocialMediaSerializer, ResourceSerializer, UnitSerializer, ImageGallerySerializer, ImageSerializer
# Create your views here.


class HomeViewSet(ModelViewSet):
    queryset = HomePage.objects.all()
    serializer_class = HomePageSerializer

    def list(self, request):
        queryset = HomePage.objects.all()
        serializer = HomePageSerializer(queryset, many=True)
        return Response(serializer.data)


class SocialMediaViewSet(ModelViewSet):
    print('social media viewset')
    queryset = SocialMedia.objects.all()
    serializer_class = SocialMediaSerializer


class ResourceViewSet(ModelViewSet):
    queryset = Resource.objects.all()
    serializer_class = ResourceSerializer
    paginate_by = 10


class UnitViewSet(ModelViewSet):
    queryset = Unit.objects.all()
    serializer_class = UnitSerializer
    paginate_by = 10


class ImageGalleryViewset(ModelViewSet):
    queryset = ImageGallery.objects.all()
    serializer_class = ImageGallerySerializer
    paginate_by = 10


class ImageViewset(ModelViewSet):
    queryset = Image.objects.all()
    serializer_class = ImageSerializer
    paginate_by = 10

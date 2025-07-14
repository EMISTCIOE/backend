# Create your views here.
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from .models import (
    Calendar,
    HomePage,
    Image,
    ImageGallery,
    Report,
    Resource,
    SocialMedia,
    Unit,
)
from .serializer import (
    CalendarSerializer,
    HomePageSerializer,
    ImageGallerySerializer,
    ImageSerializer,
    ReportSerializer,
    ResourceSerializer,
    SocialMediaSerializer,
    UnitSerializer,
)


class ReportViewset(ModelViewSet):
    queryset = Report.objects.all()
    serializer_class = ReportSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]


class CalendarViewset(ModelViewSet):
    queryset = Calendar.objects.all()
    serializer_class = CalendarSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]


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

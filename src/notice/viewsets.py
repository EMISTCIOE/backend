from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.viewsets import ModelViewSet

from .models import Notice, NoticeCategory, NoticeType
from .serializer import NoticeCategorySerializer, NoticeSerializer, NoticeTypeSerializer

# Create your views here.


class NoticeViewSet(ModelViewSet):
    queryset = Notice.objects.all()
    serializer_class = NoticeSerializer
    paginate_by = 10  # pagination is not working as of now
    permission_classes = [IsAuthenticatedOrReadOnly]


class NoticeTypeViewSet(ModelViewSet):
    queryset = NoticeType.objects.all()
    serializer_class = NoticeTypeSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]


class NoticeCategoryViewSet(ModelViewSet):
    queryset = NoticeCategory.objects.all()
    serializer_class = NoticeCategorySerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

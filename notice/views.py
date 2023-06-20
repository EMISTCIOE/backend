from django.shortcuts import render
from rest_framework.viewsets import ModelViewSet
from .models import Notice, NoticeType, NoticeCategory
from .serializer import NoticeSerializer, NoticeTypeSerializer, NoticeCategorySerializer

# Create your views here.

class NoticeViewSet(ModelViewSet):
    queryset = Notice.objects.all()
    serializer_class = NoticeSerializer

class NoticeTypeViewSet(ModelViewSet):
    queryset = NoticeType.objects.all()
    serializer_class = NoticeTypeSerializer

class NoticeCategoryViewSet(ModelViewSet):
    queryset = NoticeCategory.objects.all()
    serializer_class = NoticeCategorySerializer



    
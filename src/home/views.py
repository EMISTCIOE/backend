from django.db.models import Q
from django.shortcuts import render
from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.views import APIView

from .models import Image, Resource
from .serializer import ImageSerializer, ResourceSerializer


class ResourceSearchView(ListAPIView):
    model = Resource
    serializer_class = ResourceSerializer
    paginate_by = 10
    permission_classes = [IsAuthenticatedOrReadOnly]

    # get a query and search for it in the title and description of the Resource
    def get_queryset(self):
        keyword = self.request.GET.get("keyword", "")
        title = self.request.GET.get("title", "")

        # print(query)
        queryset = Resource.objects.all()
        if keyword:
            queryset = queryset.filter(
                Q(title__icontains=keyword) | Q(description__icontains=keyword),
            )
        if title:
            queryset = queryset.filter(title__iexact=title)
        return queryset


class ImageSearchView(ListAPIView):
    model = Image
    serializer_class = ImageSerializer
    paginate_by = 10
    permission_classes = [IsAuthenticatedOrReadOnly]

    # get a query and search for it in the title and description of the Resource
    def get_queryset(self):
        gallery_name = self.request.GET.get("gallery_name", "")
        image_name = self.request.GET.get("image_name", "")
        image_id = self.request.GET.get("image_id", "")
        queryset = Image.objects.all()
        if gallery_name:
            queryset = queryset.filter(gallery__name__icontains=gallery_name)
        if image_name:
            queryset = queryset.filter(name__icontains=image_name)
        if image_id:
            queryset = queryset.filter(id__iexact=image_id)
        return queryset

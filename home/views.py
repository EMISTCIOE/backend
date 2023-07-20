from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.generics import ListAPIView
from .models import Resource
from .serializer import ResourceSerializer
from django.db.models import Q
from rest_framework.permissions import  IsAuthenticatedOrReadOnly


class ResourceSearchView(ListAPIView):
    model = Resource
    serializer_class = ResourceSerializer
    paginate_by = 10
    permission_classes = [IsAuthenticatedOrReadOnly]

    # get a query and search for it in the title and description of the Resource
    def get_queryset(self):
        keyword = self.request.GET.get('keyword', '')
        title = self.request.GET.get('title', '')

        # print(query)
        queryset = Resource.objects.all()
        if keyword:
            queryset = queryset.filter(
                Q(title__icontains=keyword) | Q(description__icontains=keyword))
        if title:
            queryset = queryset.filter(title__iexact=title)
        return queryset

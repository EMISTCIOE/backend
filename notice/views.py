from django.shortcuts import render
from rest_framework.generics import ListAPIView
from .models import Notice
from rest_framework.response import Response
from .serializer import NoticeSerializer




class NoticeSearchView(ListAPIView):
    model = Notice
    serializer_class = NoticeSerializer

    # get a query and search for it in the title and description of the notice
    def get_queryset(self):
        query = self.request.GET.get('query', '')
        queryset = Notice.objects.all()
        if query:
            queryset = Notice.objects.filter(title__icontains=query) | Notice.objects.filter(description__icontains=query)
        return queryset
    
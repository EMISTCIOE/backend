from django.shortcuts import render
from rest_framework.generics import ListAPIView
from .models import Notice
from rest_framework.response import Response
from .serializer import NoticeSerializer
from django.db.models import Q




class NoticeSearchView(ListAPIView):
    model = Notice
    serializer_class = NoticeSerializer
    paginate_by = 10

    # get a query and search for it in the title and description of the notice
    def get_queryset(self):
        query = self.request.GET.get('query', '')
        # print(query)
        queryset = Notice.objects.all()
        if query:
            queryset = Notice.objects.filter(
                Q(title__icontains=query) | Q(description__icontains=query) | Q(slug__icontains=query)
            )
        return queryset
    
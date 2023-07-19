from django.shortcuts import render
from rest_framework.generics import ListAPIView
from .models import Notice
from rest_framework.response import Response
from .serializer import NoticeSerializer
from django.db.models import Q
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly


class NoticeSearchView(ListAPIView):
    model = Notice
    serializer_class = NoticeSerializer
    paginate_by = 10
    permission_classes = [IsAuthenticated]

    # get a query and search for it in the title and description of the notice,
    # if the query is empty then return all the notices
    # search for notices based on category, notice type, department, is_featured, published_date, start_date, end_date parameters
    def get_queryset(self):
        keyword = self.request.GET.get('keyword', '')
        category = self.request.GET.get('category', '')
        notice_type = self.request.GET.get('notice_type', '')
        department = self.request.GET.get('department', '')
        is_featured = self.request.GET.get('is_featured', '')
        published_date = self.request.GET.get('published_date', '')
        start_date = self.request.GET.get('start_date', '')
        end_date = self.request.GET.get('end_date', '')

        # print(query)
        queryset = Notice.objects.all()
        if start_date and end_date:
            queryset = queryset.filter(published_date__range=[
                                       start_date, end_date])
        if category:
            queryset = queryset.filter(
                notice_category__category__iexact=category)
        if notice_type:
            queryset = queryset.filter(
                notice_category__notice_type__notice_type__iexact=notice_type)
        if department:
            queryset = queryset.filter(department__name__icontains=department)
        if is_featured:
            queryset = queryset.filter(is_featured__iexact=is_featured)
        if published_date:
            queryset = queryset.filter(
                published_date__icontains=published_date)
        if keyword:
            queryset = queryset.filter(
                Q(title__icontains=keyword) | Q(description__icontains=keyword))
        return queryset

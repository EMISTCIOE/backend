from django.shortcuts import render
from rest_framework.generics import ListAPIView, RetrieveAPIView, CreateAPIView
from django.db.models import Q
from .models import Article, BoardMember, ArticleXml
from .serializers import ArticleSerializer, BoardMemberSerializer, ArticleXmlSerializer
from rest_framework.permissions import IsAuthenticatedOrReadOnly
# Create your views here.


class ArticleSearchView(ListAPIView):
    model = Article
    serializer_class = ArticleSerializer
    paginate_by = 10
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        url_id = self.request.GET.get('url_id', '').lower()
        title = self.request.GET.get('title', '').lower()
        genre = self.request.GET.get('genre', '').lower()
        doi_id = self.request.GET.get('doi_id', '').lower()
        queryset = Article.objects.all()
        if url_id:
            queryset = queryset.filter(url_id__iexact=url_id)
        if title:
            queryset = queryset.filter(title__icontains=title)
        if genre:
            queryset = queryset.filter(genre__icontains=genre)
        if doi_id:
            queryset = queryset.filter(doi_id__iexact=doi_id)
        return queryset


class BoardMemberSearchView(ListAPIView):
    model = BoardMember
    serializer_class = BoardMemberSerializer
    paginate_by = 10
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        name = self.request.GET.get('name', '').lower()
        designation = self.request.GET.get('designation', '').lower()
        department = self.request.GET.get('department', '').lower()
        queryset = BoardMember.objects.all()
        if name:
            queryset = queryset.filter(name__icontains=name)
        if designation:
            queryset = queryset.filter(designation__icontains=designation)
        if department:
            queryset = queryset.filter(department__icontains=department)
        return queryset


class ArticleXMLPostView(CreateAPIView):
    model = ArticleXml
    serializer_class = ArticleXmlSerializer
    # permission_classes = [IsAuthenticatedOrReadOnly]

    def post(self, request, *args, **kwargs):
        # edit before saving

        return self.create(request, *args, **kwargs)

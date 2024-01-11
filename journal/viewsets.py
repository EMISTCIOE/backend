from rest_framework import viewsets
from .models import Article, Author, BoardMember
from .serializers import ArticleSerializer, AuthorSerializer, BoardMemberSerializer
from rest_framework.permissions import IsAuthenticatedOrReadOnly


class ArticleViewsets(viewsets.ModelViewSet):
    queryset = Article.objects.all()
    serializer_class = ArticleSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]


class BoardMemberViewset(viewsets.ModelViewSet):
    queryset = BoardMember.objects.all()
    serializer_class = BoardMemberSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

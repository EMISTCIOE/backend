from rest_framework import viewsets, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django_filters.rest_framework import DjangoFilterBackend

from ..models import Article
from ..serializers import ArticleSerializer


class PublicArticleViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Public read-only API for journal articles.
    """
    permission_classes = [AllowAny]
    queryset = Article.objects.select_related("department").prefetch_related("authors").all()
    serializer_class = ArticleSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ["department__slug", "genre"]
    search_fields = ["title", "abstract", "keywords", "discipline", "authors__given_name", "authors__family_name"]
    ordering_fields = ["date_published", "title"]
    ordering = ["-date_published"]

    @action(detail=False, methods=["get"])
    def featured(self, request):
        featured_articles = self.get_queryset()[:6]
        serializer = self.get_serializer(featured_articles, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["get"])
    def by_department(self, request):
        slug = request.query_params.get("department_slug")
        if not slug:
            return Response({"error": "department_slug parameter is required"}, status=400)
        articles = self.get_queryset().filter(department__slug=slug)
        serializer = self.get_serializer(articles, many=True)
        return Response(serializer.data)

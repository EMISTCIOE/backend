from rest_framework import serializers
from .models import Article, Author, BoardMember


class AuthorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Author
        fields = "__all__"


class ArticleSerializer(serializers.ModelSerializer):
    authors = AuthorSerializer(many=True, read_only=True)

    class Meta:
        model = Article
        fields = ["id", "url_id", "title", "genre", "date_published", "doi_id", "abstract",
                  "keywords", "discipline", "authors", "submission_id", "volume", "number", "year", "pages"]


class BoardMemberSerializer(serializers.ModelSerializer):
    class Meta:
        model = BoardMember
        fields = "__all__"

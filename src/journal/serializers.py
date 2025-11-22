from rest_framework import serializers

from .models import Article, ArticleXml, Author, BoardMember


class AuthorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Author
        fields = "__all__"


class ArticleSerializer(serializers.ModelSerializer):
    authors = AuthorSerializer(many=True, read_only=True)
    author_ids = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Author.objects.all(),
        write_only=True,
        required=False,
        allow_empty=True,
    )
    department_name = serializers.CharField(
        source="department.name", read_only=True, allow_null=True
    )
    academic_program_name = serializers.CharField(
        source="academic_program.name", read_only=True, allow_null=True
    )
    academic_program_short_name = serializers.CharField(
        source="academic_program.short_name", read_only=True, allow_null=True
    )

    class Meta:
        model = Article
        fields = [
            "id",
            "url_id",
            "title",
            "genre",
            "date_published",
            "doi_id",
            "abstract",
            "keywords",
            "discipline",
            "department",
            "department_name",
            "academic_program",
            "academic_program_name",
            "academic_program_short_name",
            "authors",
            "author_ids",
            "submission_id",
            "volume",
            "number",
            "year",
            "pages",
        ]

    def create(self, validated_data):
        author_ids = validated_data.pop("author_ids", [])
        article = super().create(validated_data)
        if author_ids:
            article.authors.set(author_ids)
        return article

    def update(self, instance, validated_data):
        author_ids = validated_data.pop("author_ids", None)
        article = super().update(instance, validated_data)
        if author_ids is not None:
            article.authors.set(author_ids)
        return article


class BoardMemberSerializer(serializers.ModelSerializer):
    class Meta:
        model = BoardMember
        fields = "__all__"


class ArticleXmlSerializer(serializers.ModelSerializer):
    class Meta:
        model = ArticleXml
        fields = "__all__"

import uuid

from django.core.validators import FileExtensionValidator
from django.db import models
from django.urls import reverse

# Create your models here.


class Author(models.Model):
    given_name = models.CharField(max_length=200, verbose_name="Given Name")
    family_name = models.CharField(
        max_length=200,
        verbose_name="Family Name",
        null=True,
        blank=True,
    )
    affiliation = models.CharField(max_length=500, null=True, blank=True)
    country = models.CharField(max_length=200, null=True, blank=True)
    email = models.EmailField(null=True, blank=True)
    bio = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"{self.given_name} {self.family_name}"

    def get_absolute_url(self):
        return reverse("author_detail", kwargs={"pk": self.pk})

    class Meta:
        ordering = ["family_name", "given_name"]


class Article(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    url_id = models.CharField(max_length=50)
    title = models.CharField(max_length=500)
    genre = models.CharField(max_length=500)
    date_published = models.DateField(
        verbose_name="Published Date",
        null=True,
        blank=True,
    )
    doi_id = models.CharField(
        max_length=500,
        verbose_name="DOI ID",
        null=True,
        blank=True,
    )
    abstract = models.TextField()
    keywords = models.CharField(max_length=500, null=True, blank=True)
    discipline = models.CharField(max_length=500, null=True, blank=True)
    authors = models.ManyToManyField(Author, related_name="article_author")
    submission_id = models.IntegerField(
        verbose_name="Submission ID",
        null=True,
        blank=True,
    )
    volume = models.IntegerField(null=True, blank=True)
    number = models.IntegerField(null=True, blank=True)
    year = models.IntegerField(null=True, blank=True)
    pages = models.CharField(max_length=40, null=True, blank=True)

    def __str__(self):
        return self.title

    def get_author(self):
        return ", ".join([str(p) for p in self.authors.all()])

    # def get_absolute_url(self):
    #     return reverse("api/journal/article", kwargs={"pk": self.pk})

    class Meta:
        ordering = ["title"]
        unique_together = ["url_id"]


class BoardMember(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200)
    image = models.ImageField(
        upload_to="media/editorial_board/images",
        null=True,
        blank=True,
    )
    role = models.CharField(max_length=200)
    rank = models.IntegerField(null=True, blank=True)
    designation = models.CharField(max_length=200)
    department = models.CharField(max_length=500)
    organization = models.CharField(max_length=500)
    email = models.EmailField()
    orcid_id = models.CharField(
        max_length=50,
        verbose_name="ORCID iD",
        null=True,
        blank=True,
    )
    google_scholar_link = models.URLField(
        null=True,
        blank=True,
        verbose_name="Google Scholar Profile",
    )
    research_gate_link = models.URLField(
        null=True,
        blank=True,
        verbose_name="Research Gate Profile",
    )

    def __str__(self):
        return self.name.title() + "-" + str(self.role)

    class Meta:
        ordering = ["-rank", "designation"]
        verbose_name = "Board Member"


class ArticleXml(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    article_name = models.CharField(max_length=500, null=True, blank=True, unique=True)
    xml_file = models.FileField(
        upload_to="xmls/articles/",
        null=True,
        blank=True,
        validators=[
            FileExtensionValidator(
                [
                    "xml",
                ],
            ),
        ],
    )

    def __str__(self):
        # return file name only not the path
        return (
            str(self.article_name.title())
            if self.article_name != None
            else "Article XML"
        )

    class Meta:
        ordering = ["-article_name"]
        verbose_name = "Article XML"

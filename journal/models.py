from django.db import models
import uuid

# Create your models here.


class Author(models.Model):
    given_name = models.CharField(max_length=100, verbose_name="Given Name")
    family_name = models.CharField(max_length=100, verbose_name="Family Name")
    affiliation = models.CharField(max_length=100)
    country = models.CharField(max_length=100)
    email = models.EmailField()
    bio = models.TextField()

    def __str__(self):
        return f"{self.given_name} {self.family_name}"

    def get_absolute_url(self):
        return reverse("author_detail", kwargs={"pk": self.pk})

    class Meta:
        ordering = ["family_name", "given_name"]


class Article(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    url_id = models.IntegerField(blank=False, null=False)
    title = models.CharField(max_length=100, blank=False, null=False)
    genre = models.CharField(max_length=100, blank=False, null=False)
    date_published = models.DateField(
        blank=False, null=False, verbose_name="Published Date")
    doi_id = models.CharField(max_length=100, verbose_name="DOI ID")
    abstract = models.TextField()
    keywords = models.CharField(max_length=100)
    discipline = models.CharField(max_length=100)
    authors = models.ManyToManyField(Author)
    submission_id = models.IntegerField(verbose_name="Submission ID")
    volume = models.IntegerField()
    number = models.IntegerField()
    year = models.IntegerField()
    pages = models.CharField(max_length=20)

    def __str__(self):
        return self.title

    def get_author(self):
        return ", ".join([str(p) for p in self.authors.all()])

    def get_absolute_url(self):
        return reverse("article_detail", kwargs={"pk": self.pk})

    class Meta:
        ordering = ["title"]


class BoardMember(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    image = models.ImageField(
        upload_to="media/editorial_board/images", null=True, blank=True)
    role = models.CharField(max_length=100)
    designation = models.CharField(max_length=100)
    department = models.CharField(max_length=100)
    organization = models.CharField(max_length=100)
    email = models.EmailField()
    link = models.URLField(null=True, blank=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ["designation"]

from django.contrib import admin
from .models import Author, Article, BoardMember
# Register your models here.


class ArticleAdmin(admin.ModelAdmin):
    list_display = ("title", "genre", "date_published")
    list_filter = ("title", "genre", "date_published")
    search_fields = ("title", "genre", "date_published")


admin.site.register(Article, ArticleAdmin)
admin.site.register(Author)
admin.site.register(BoardMember)

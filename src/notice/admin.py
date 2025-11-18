from django.contrib import admin

from .models import Notice, NoticeCategory, NoticeMedia


class NoticeMediaInline(admin.TabularInline):
    """Allow attaching multiple media files directly while editing a notice."""

    model = NoticeMedia
    extra = 1
    fields = ("file", "media_type", "caption")


@admin.register(Notice)
class NoticeAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "category",
        "department",
        "status",
        "published_at",
        "is_featured",
    )
    list_filter = ("status", "category", "department", "is_featured")
    search_fields = ("title",)
    inlines = [NoticeMediaInline]

    def save_formset(self, request, form, formset, change):
        instances = formset.save(commit=False)
        for obj in instances:
            if not obj.pk:
                obj.created_by = request.user
            obj.updated_by = request.user
            obj.save()
        formset.save_m2m()


admin.site.register(NoticeCategory)
admin.site.register(NoticeMedia)

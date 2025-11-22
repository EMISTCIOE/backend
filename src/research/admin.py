from django.contrib import admin

from .models import (
    Research,
    ResearchCategory,
    ResearchCategoryAssignment,
    ResearchParticipant,
    ResearchPublication,
)


class ResearchParticipantInline(admin.TabularInline):
    model = ResearchParticipant
    extra = 1
    fields = ("full_name", "participant_type", "role", "email", "department")


class ResearchPublicationInline(admin.TabularInline):
    model = ResearchPublication
    extra = 1
    fields = ("title", "journal_conference", "publication_date", "doi")


class ResearchCategoryAssignmentInline(admin.TabularInline):
    model = ResearchCategoryAssignment
    extra = 1


@admin.register(Research)
class ResearchAdmin(admin.ModelAdmin):
    list_display = [
        "title",
        "research_type",
        "status",
        "principal_investigator",
        "funding_agency",
        "funding_amount",
        "is_featured",
        "is_published",
        "views_count",
        "created_at",
    ]
    list_filter = [
        "research_type",
        "status",
        "is_featured",
        "is_published",
        "funding_agency",
        "created_at",
    ]
    search_fields = [
        "title",
        "abstract",
        "description",
        "keywords",
        "funding_agency",
        "principal_investigator",
    ]
    readonly_fields = [
        "views_count",
        "created_at",
        "updated_at",
        "created_by",
        "updated_by",
        "uuid",
    ]

    fieldsets = (
        (
            "Basic Information",
            {
                "fields": (
                    "title",
                    "abstract",
                    "description",
                    "research_type",
                    "status",
                    "keywords",
                ),
            },
        ),
        (
            "Principal Investigator",
            {"fields": ("principal_investigator", "pi_email", "department")},
        ),
        ("Methodology & Outcomes", {"fields": ("methodology", "expected_outcomes")}),
        ("Timeline", {"fields": ("start_date", "end_date")}),
        ("Funding Information", {"fields": ("funding_agency", "funding_amount")}),
        (
            "External Links & Files",
            {
                "fields": (
                    "github_url",
                    "project_url",
                    "publications_url",
                    "report_file",
                    "thumbnail",
                ),
            },
        ),
        ("Publishing", {"fields": ("is_featured", "is_published")}),
        (
            "Metadata",
            {
                "fields": (
                    "views_count",
                    "created_at",
                    "updated_at",
                    "created_by",
                    "updated_by",
                ),
                "classes": ("collapse",),
            },
        ),
    )

    inlines = [
        ResearchParticipantInline,
        ResearchPublicationInline,
        ResearchCategoryAssignmentInline,
    ]

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("department")

    def save_model(self, request, obj, form, change):
        if not change or not obj.created_by_id:
            obj.created_by = request.user
        obj.updated_by = request.user
        super().save_model(request, obj, form, change)

    def save_formset(self, request, form, formset, change):
        instances = formset.save(commit=False)
        for inline_obj in instances:
            if hasattr(inline_obj, "created_by") and not getattr(
                inline_obj, "created_by_id", None
            ):
                inline_obj.created_by = request.user
            if hasattr(inline_obj, "updated_by"):
                inline_obj.updated_by = request.user
            inline_obj.save()
        formset.save_m2m()


@admin.register(ResearchParticipant)
class ResearchParticipantAdmin(admin.ModelAdmin):
    list_display = ["full_name", "participant_type", "role", "organization", "research"]
    list_filter = ["participant_type", "role", "department"]
    search_fields = ["full_name", "organization", "email", "designation"]
    readonly_fields = [
        "created_at",
        "updated_at",
        "created_by",
        "updated_by",
        "uuid",
    ]

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("research")

    def save_model(self, request, obj, form, change):
        if not change or not obj.created_by_id:
            obj.created_by = request.user
        obj.updated_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(ResearchPublication)
class ResearchPublicationAdmin(admin.ModelAdmin):
    list_display = [
        "title",
        "journal_conference",
        "publication_date",
        "citation_count",
        "research",
    ]
    list_filter = ["publication_date"]
    search_fields = ["title", "journal_conference", "doi"]
    date_hierarchy = "publication_date"
    readonly_fields = [
        "created_at",
        "updated_at",
        "created_by",
        "updated_by",
        "uuid",
    ]

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("research")

    def save_model(self, request, obj, form, change):
        if not change or not obj.created_by_id:
            obj.created_by = request.user
        obj.updated_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(ResearchCategory)
class ResearchCategoryAdmin(admin.ModelAdmin):
    list_display = ["name", "slug", "color", "research_count"]
    search_fields = ["name", "slug"]
    prepopulated_fields = {"slug": ("name",)}
    readonly_fields = [
        "created_at",
        "updated_at",
        "created_by",
        "updated_by",
        "uuid",
    ]

    def research_count(self, obj):
        return obj.researchcategoryassignment_set.count()

    research_count.short_description = "Research Count"

    def save_model(self, request, obj, form, change):
        if not change or not obj.created_by_id:
            obj.created_by = request.user
        obj.updated_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(ResearchCategoryAssignment)
class ResearchCategoryAssignmentAdmin(admin.ModelAdmin):
    list_display = ["research", "category"]
    list_filter = ["category"]

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("research", "category")

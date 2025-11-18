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
    readonly_fields = ["views_count", "created_at", "updated_at"]

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
                "fields": ("views_count", "created_at", "updated_at"),
                "classes": ("collapse",),
            },
        ),
    )

    inlines = [
        ResearchParticipantInline,
        ResearchPublicationInline,
        ResearchCategoryAssignmentInline,
    ]


@admin.register(ResearchParticipant)
class ResearchParticipantAdmin(admin.ModelAdmin):
    list_display = ["full_name", "participant_type", "role", "organization", "research"]
    list_filter = ["participant_type", "role", "department"]
    search_fields = ["full_name", "organization", "email", "designation"]

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("research")


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

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("research")


@admin.register(ResearchCategory)
class ResearchCategoryAdmin(admin.ModelAdmin):
    list_display = ["name", "slug", "color", "research_count"]
    search_fields = ["name", "slug"]
    prepopulated_fields = {"slug": ("name",)}

    def research_count(self, obj):
        return obj.researchcategoryassignment_set.count()

    research_count.short_description = "Research Count"


@admin.register(ResearchCategoryAssignment)
class ResearchCategoryAssignmentAdmin(admin.ModelAdmin):
    list_display = ["research", "category"]
    list_filter = ["category"]

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("research", "category")

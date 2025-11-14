from django.contrib import admin
from .models import Project, ProjectMember, ProjectTag, ProjectTagAssignment


class ProjectMemberInline(admin.TabularInline):
    model = ProjectMember
    extra = 1
    fields = ('full_name', 'roll_number', 'email', 'role', 'department')


class ProjectTagAssignmentInline(admin.TabularInline):
    model = ProjectTagAssignment
    extra = 1


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = [
        'title',
        'project_type',
        'status',
        'supervisor_name',
        'academic_year',
        'is_featured',
        'is_published',
        'views_count',
        'created_at'
    ]
    list_filter = [
        'project_type',
        'status',
        'is_featured',
        'is_published',
        'academic_year',
        'created_at'
    ]
    search_fields = [
        'title',
        'description',
        'abstract',
        'supervisor_name',
        'technologies_used'
    ]
    readonly_fields = ['views_count', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': (
                'title',
                'description',
                'abstract',
                'project_type',
                'status'
            )
        }),
        ('Academic Details', {
            'fields': (
                'department',
                'supervisor_name',
                'supervisor_email',
                'academic_year'
            )
        }),
        ('Timeline', {
            'fields': (
                'start_date',
                'end_date'
            )
        }),
        ('External Links & Files', {
            'fields': (
                'github_url',
                'demo_url',
                'report_file',
                'thumbnail'
            )
        }),
        ('Technical Details', {
            'fields': (
                'technologies_used',
            )
        }),
        ('Publishing', {
            'fields': (
                'is_featured',
                'is_published'
            )
        }),
        ('Metadata', {
            'fields': (
                'views_count',
                'created_at',
                'updated_at'
            ),
            'classes': ('collapse',)
        })
    )
    
    inlines = [ProjectMemberInline, ProjectTagAssignmentInline]
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('department')


@admin.register(ProjectMember)
class ProjectMemberAdmin(admin.ModelAdmin):
    list_display = [
        'full_name',
        'roll_number',
        'email',
        'role',
        'project',
        'department'
    ]
    list_filter = ['role', 'department']
    search_fields = ['full_name', 'roll_number', 'email']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('project', 'department')


@admin.register(ProjectTag)
class ProjectTagAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'color', 'project_count']
    search_fields = ['name', 'slug']
    prepopulated_fields = {'slug': ('name',)}
    
    def project_count(self, obj):
        return obj.projecttagassignment_set.count()
    project_count.short_description = 'Projects Count'


@admin.register(ProjectTagAssignment)
class ProjectTagAssignmentAdmin(admin.ModelAdmin):
    list_display = ['project', 'tag']
    list_filter = ['tag']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('project', 'tag')
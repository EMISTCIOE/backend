from django.contrib import admin

from .models import Project, ProjectCategory, ProjectRating, ProjectTeamMember

admin.site.register(ProjectCategory)
admin.site.register(Project)
admin.site.register(Project)
admin.site.register(ProjectRating)
admin.site.register(ProjectTeamMember)

from django.urls import include, path

app_label = ["public"]

urlpatterns = [
    path("user-mod/", include("src.user.public.urls")),
    path("notice-mod/", include("src.notice.public.urls")),
    path("website-mod/", include("src.website.public.urls")),
    path("department-mod/", include("src.department.public.urls")),
    path("project-hive-mod/", include("src.project_hive.public.urls")),
]

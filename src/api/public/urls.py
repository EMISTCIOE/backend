from django.urls import include, path

app_label = ["public"]

urlpatterns = [
    path("home-mod/", include("src.home.urls")),
    path("notice-mod/", include("src.notice.urls")),
    path("department-mod/", include("src.department.urls")),
    path("curriculum-mod/", include("src.curriculum.urls")),
    path("journal-mod/", include("src.journal.urls")),
]

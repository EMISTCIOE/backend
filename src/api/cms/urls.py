from django.urls import include, path

app_label = ["admin"]

urlpatterns = [
    path("user-mod/", include("src.user.urls")),
    path("notice-mod/", include("src.notice.urls")),
    path("website-mod/", include("src.website.urls")),
    path("department-mod/", include("src.department.urls")),
    # path("curriculum-mod/", include("src.curriculum.urls")),
    # path("journal-mod/", include("src.journal.urls")),
]

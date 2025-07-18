from django.urls import include, path

app_label = ["public"]

urlpatterns = [
    path("user-mod/", include("src.user.public.urls")),
    path("notice-mod/", include("src.notice.public.urls")),
    path("website-mod/", include("src.website.urls")),
]

from django.urls import include, path

app_label = ["public"]

urlpatterns = [
    path("user-mod/", include("src.user.public.urls")),
    path("home-mod/", include("src.home.urls")),
    path("notice-mod/", include("src.notice.public.urls")),
]

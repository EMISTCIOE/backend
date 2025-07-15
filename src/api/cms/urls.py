from django.urls import include, path

app_label = ["admin"]

urlpatterns = [
    path("user-mod/", include("src.user.urls")),
]

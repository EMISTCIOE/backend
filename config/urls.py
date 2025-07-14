# ruff: noqa
"""URL Configuration"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)
from django.views.generic import TemplateView


class CustomSpectacularSwaggerView(SpectacularSwaggerView):
    def dispatch(self, request, *args, **kwargs):
        from django.shortcuts import redirect
        from rest_framework.reverse import reverse

        response = super().dispatch(request, *args, **kwargs)
        if response.status_code == 401:
            # Redirect the user to the login page if not authenticated
            return redirect(reverse("rest_framework:login") + f"?next={request.path}")
        return response


urlpatterns = [
    path("api/", include("home.urls")),
    path("api/notice/", include("notice.urls")),
    path("api/department/", include("department.urls")),
    path("api/curriculum/", include("curriculum.urls")),
    path("api/journal/", include("journal.urls")),
    # Django Admin, use {% url 'admin:index' %}
    path(settings.ADMIN_URL, admin.site.urls),
    # Media files
    *static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT),
]


if settings.DEBUG:
    # Static file serving when using Gunicorn + Uvicorn for local web socket development
    urlpatterns += staticfiles_urlpatterns()


# API URLS
urlpatterns += [
    path("", TemplateView.as_view(template_name="pages/home.html"), name="home"),
    # DRF auth token
    path("api-auth/", include("rest_framework.urls")),
    path("api/schema/", SpectacularAPIView.as_view(), name="api-schema"),
    path(
        "api/docs/",
        CustomSpectacularSwaggerView.as_view(url_name="api-schema"),
        name="swagger-ui",
    ),
    path(
        "api/redoc/",
        SpectacularRedocView.as_view(url_name="api-schema"),
        name="redoc-ui",
    ),
]

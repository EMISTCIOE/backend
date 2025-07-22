from django.urls import include, path
from rest_framework import routers

from .views import (
    PublicNoticeCategoryListAPIView,
    PublicNoticeDepartmentListAPIView,
    PublicNoticeListAPIView,
    PublicNoticeRetrieveAPIView,
    PublicNoticeSetSharedAPIView,
    PublicNoticeSetViewedAPIView,
)

router = routers.DefaultRouter()

urlpatterns = [
    path(
        "notices",
        PublicNoticeListAPIView.as_view(),
        name="public_list_notices",
    ),
    path(
        "notices/<uuid:notice_id>",
        PublicNoticeRetrieveAPIView.as_view(),
        name="public_retrieve_notices",
    ),
    path(
        "notices/<uuid:notice_id>/view",
        PublicNoticeSetViewedAPIView.as_view(),
        name="public_notice_view",
    ),
    path(
        "notices/<uuid:notice_id>/share",
        PublicNoticeSetSharedAPIView.as_view(),
        name="public_notice_share",
    ),
    path("", include(router.urls)),
    # Listing APIs
    path(
        "notices/categories",
        PublicNoticeCategoryListAPIView.as_view(),
        name="public_list_notice_categories",
    ),
    path(
        "notices/departments",
        PublicNoticeDepartmentListAPIView.as_view(),
        name="public_list_notice_departments",
    ),
]

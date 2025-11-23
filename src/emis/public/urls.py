from django.urls import path

from .views import (
    PublicEMISDownloadListAPIView,
    PublicEMISNoticeListAPIView,
    PublicEMISNoticeRetrieveAPIView,
    PublicEMISNoticeSetViewedAPIView,
)

urlpatterns = [
    path("downloads", PublicEMISDownloadListAPIView.as_view(), name="public_emis_downloads"),
    path("notices", PublicEMISNoticeListAPIView.as_view(), name="public_emis_notices"),
    path(
        "notices/<slug:notice_id>",
        PublicEMISNoticeRetrieveAPIView.as_view(),
        name="public_emis_notice_detail",
    ),
    path(
        "notices/<slug:notice_id>/view",
        PublicEMISNoticeSetViewedAPIView.as_view(),
        name="public_emis_notice_view",
    ),
]

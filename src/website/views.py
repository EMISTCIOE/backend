import django_filters
from django.db import transaction
from django_filters.filterset import FilterSet
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema
from rest_framework import generics, status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import NotFound
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ReadOnlyModelViewSet

# Project Imports
from src.libs.utils import set_binary_files_null_if_empty
from src.website.messages import (
    ACADEMIC_CALENDER_DELETED_SUCCESS,
    ACADEMIC_CALENDER_NOT_FOUND,
    CAMPUS_CLUB_DELETED_SUCCESS,
    CAMPUS_CLUB_NOT_FOUND,
    CAMPUS_DOWNLOAD_DELETED_SUCCESS,
    CAMPUS_DOWNLOAD_NOT_FOUND,
    CAMPUS_EVENT_DELETED_SUCCESS,
    CAMPUS_EVENT_NOT_FOUND,
    CAMPUS_FEEDBACK_RESOLVE_SUCCESS,
    CAMPUS_INFO_NOT_FOUND,
    CAMPUS_REPORT_DELETED_SUCCESS,
    CAMPUS_REPORT_NOT_FOUND,
    CAMPUS_UNION_DELETED_SUCCESS,
    CAMPUS_UNION_NOT_FOUND,
    EVENT_GALLERY_DELETED_SUCCESS,
    EVENT_GALLERY_NOT_FOUND,
    MEMBER_DELETED_SUCCESS,
    MEMBER_NOT_FOUND,
    SOCIAL_MEDIA_DELETED_SUCCESS,
    SOCIAL_MEDIA_NOT_FOUND,
)

from .models import (
    AcademicCalendar,
    CampusDownload,
    CampusEvent,
    CampusEventGallery,
    CampusFeedback,
    CampusInfo,
    CampusKeyOfficial,
    CampusReport,
    CampusUnion,
    CampusUnionMember,
    SocialMediaLink,
    StudentClub,
    StudentClubMember,
)
from .permissions import (
    AcademicCalendarPermission,
    CampusClubPermission,
    CampusDownloadPermission,
    CampusEventPermission,
    CampusFeedbackPermission,
    CampusInfoPermission,
    CampusKeyOfficialPermission,
    CampusReportPermission,
    CampusUnionPermission,
)
from .serializers import (
    AcademicCalendarCreateSerializer,
    AcademicCalendarListSerializer,
    AcademicCalendarPatchSerializer,
    AcademicCalendarRetrieveSerializer,
    CampusDownloadCreateSerializer,
    CampusDownloadListSerializer,
    CampusDownloadPatchSerializer,
    CampusDownloadRetrieveSerializer,
    CampusEventCreateSerializer,
    CampusEventListSerializer,
    CampusEventPatchSerializer,
    CampusEventRetrieveSerializer,
    CampusFeedbackListSerializer,
    CampusFeedbackResolveSerializer,
    CampusInfoPatchSerializer,
    CampusInfoRetrieveSerializer,
    CampusKeyOfficialCreateSerializer,
    CampusKeyOfficialListSerializer,
    CampusKeyOfficialPatchSerializer,
    CampusKeyOfficialRetrieveSerializer,
    CampusReportCreateSerializer,
    CampusReportListSerializer,
    CampusReportPatchSerializer,
    CampusReportRetrieveSerializer,
    CampusUnionCreateSerializer,
    CampusUnionListSerializer,
    CampusUnionPatchSerializer,
    CampusUnionRetrieveSerializer,
    StudentClubCreateSerializer,
    StudentClubListSerializer,
    StudentClubPatchSerializer,
    StudentClubRetrieveSerializer,
)


class CampusInfoAPIView(generics.GenericAPIView):
    """Campus Info Retrive and Update APIs"""

    permission_classes = [CampusInfoPermission]

    def get_serializer_class(self):
        if self.request.method == "PATCH":
            return CampusInfoPatchSerializer
        return CampusInfoRetrieveSerializer

    def get_object(self):
        return CampusInfo.objects.filter(is_archived=False).first()

    def get(self, request, *args, **kwargs):
        instance = self.get_object()
        if not instance:
            return Response(
                {"detail": CAMPUS_INFO_NOT_FOUND},
                status=status.HTTP_404_NOT_FOUND,
            )
        serializer = self.get_serializer(instance, context={"request": request})
        return Response(serializer.data, status=status.HTTP_200_OK)

    @transaction.atomic
    def patch(self, request, *args, **kwargs):
        instance = self.get_object()
        if not instance:
            return Response(
                {"detail": CAMPUS_INFO_NOT_FOUND},
                status=status.HTTP_404_NOT_FOUND,
            )
        serializer = CampusInfoPatchSerializer(
            instance,
            data=request.data,
            partial=True,
            context={"request": request},
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)


class SocialMediaLinkDeleteAPIView(APIView):
    permission_classes = [CampusInfoPermission]

    def delete(self, request, pk):
        try:
            link = SocialMediaLink.objects.get(pk=pk)
        except SocialMediaLink.DoesNotExist:
            return Response(
                {"detail": SOCIAL_MEDIA_NOT_FOUND},
                status=status.HTTP_404_NOT_FOUND,
            )

        link.delete()
        return Response(
            {"message": SOCIAL_MEDIA_DELETED_SUCCESS},
            status=status.HTTP_200_OK,
        )


class CampusKeyOfficialViewSet(viewsets.ModelViewSet):
    """Campus Key Officials CRUD APIs"""

    permission_classes = [CampusKeyOfficialPermission]
    queryset = CampusKeyOfficial.objects.filter(is_archived=False)
    filter_backends = [SearchFilter, OrderingFilter, DjangoFilterBackend]
    search_fields = ["full_name", "designation", "email"]
    ordering_fields = ["full_name", "created_at", "display_order"]
    ordering = ["display_order", "-created_at"]
    filterset_fields = ["designation", "is_active"]
    http_method_names = ["get", "post", "patch", "delete", "head", "options"]

    def get_serializer_class(self):
        if self.request.method == "GET":
            if self.action == "list":
                return CampusKeyOfficialListSerializer
            else:
                return CampusKeyOfficialRetrieveSerializer
        elif self.request.method == "POST":
            return CampusKeyOfficialCreateSerializer
        elif self.request.method == "PATCH":
            return CampusKeyOfficialPatchSerializer

        return CampusKeyOfficialListSerializer

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()

        # Delete associated file if exists
        if instance.photo:
            instance.photo.delete(save=False)

        return super().destroy(request, *args, **kwargs)


class FilterForCampusFeedbackViewSet(FilterSet):
    class Meta:
        model = CampusFeedback
        fields = ["is_resolved"]


class CampusFeedbackViewSet(ReadOnlyModelViewSet):
    permission_classes = [CampusFeedbackPermission]
    queryset = CampusFeedback.objects.filter(is_archived=False)
    serializer_class = CampusFeedbackListSerializer
    filterset_class = FilterForCampusFeedbackViewSet
    filter_backends = (SearchFilter, OrderingFilter, DjangoFilterBackend)
    search_fields = ["full_name", "roll_number", "email", "message"]
    ordering_fields = ["-created_at", "full_name", "is_resolved"]
    http_method_names = ["options", "head", "get", "patch"]

    @extend_schema(
        request=CampusFeedbackResolveSerializer,
        responses={200: {"message": CAMPUS_FEEDBACK_RESOLVE_SUCCESS}},
    )
    @action(detail=True, methods=["patch"], url_path="resolve")
    def resolve(self, request, pk=None):
        instance = self.get_object()
        serializer = CampusFeedbackResolveSerializer(
            instance,
            data=request.data,
            partial=True,
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            {"message": CAMPUS_FEEDBACK_RESOLVE_SUCCESS},
            status=status.HTTP_200_OK,
        )


class FilterForCampusDownloadViewSet(FilterSet):
    date = django_filters.DateFromToRangeFilter(field_name="created_at")

    class Meta:
        model = CampusDownload
        fields = ["is_active", "date"]


class CampusDownloadViewSet(viewsets.ModelViewSet):
    permission_classes = [CampusDownloadPermission]
    filterset_class = FilterForCampusDownloadViewSet
    filter_backends = (SearchFilter, OrderingFilter, DjangoFilterBackend)
    search_fields = ["title", "description"]
    queryset = CampusDownload.objects.filter(is_archived=False)
    ordering_fields = ["-created_at", "title"]
    http_method_names = ["options", "head", "get", "patch", "post", "delete"]

    def get_serializer_class(self):
        if self.request.method == "GET":
            return (
                CampusDownloadListSerializer
                if self.action == "list"
                else CampusDownloadRetrieveSerializer
            )
        if self.request.method == "POST":
            return CampusDownloadCreateSerializer
        if self.request.method == "PATCH":
            return CampusDownloadPatchSerializer
        return CampusDownloadRetrieveSerializer

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        set_binary_files_null_if_empty(["file"], request.data)
        return super().create(request, *args, **kwargs)

    @transaction.atomic
    def update(self, request, *args, **kwargs):
        set_binary_files_null_if_empty(["file"], request.data)
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            instance.file.delete(save=False)

        except Exception:
            return Response(
                {"message": CAMPUS_DOWNLOAD_NOT_FOUND},
                status=status.HTTP_404_NOT_FOUND,
            )

        instance.delete()
        return Response(
            {"message": CAMPUS_DOWNLOAD_DELETED_SUCCESS},
            status=status.HTTP_200_OK,
        )


class FilterForCampusReportViewSet(FilterSet):
    class Meta:
        model = CampusReport
        fields = ["report_type", "fiscal_session", "is_active"]


class CampusReportViewSet(viewsets.ModelViewSet):
    permission_classes = [CampusReportPermission]
    filterset_class = FilterForCampusReportViewSet
    filter_backends = (SearchFilter, OrderingFilter, DjangoFilterBackend)
    search_fields = ["report_type", "fiscal_session__name"]
    queryset = CampusReport.objects.filter(is_archived=False)
    ordering_fields = ["-created_at", "published_date"]
    http_method_names = ["options", "head", "get", "patch", "post", "delete"]

    def get_serializer_class(self):
        if self.request.method == "GET":
            return (
                CampusReportListSerializer
                if self.action == "list"
                else CampusReportRetrieveSerializer
            )
        if self.request.method == "POST":
            return CampusReportCreateSerializer
        if self.request.method == "PATCH":
            return CampusReportPatchSerializer
        return CampusReportRetrieveSerializer

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        set_binary_files_null_if_empty(["file"], request.data)
        return super().create(request, *args, **kwargs)

    @transaction.atomic
    def update(self, request, *args, **kwargs):
        set_binary_files_null_if_empty(["file"], request.data)
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            instance.file.delete(save=False)
        except Exception:
            return Response(
                {"message": CAMPUS_REPORT_NOT_FOUND},
                status=status.HTTP_404_NOT_FOUND,
            )

        instance.delete()
        return Response(
            {"message": CAMPUS_REPORT_DELETED_SUCCESS},
            status=status.HTTP_200_OK,
        )


class FilterForAcademicCalendarViewSet(FilterSet):
    class Meta:
        model = AcademicCalendar
        fields = ["program_type", "start_year", "end_year", "is_active"]


class AcademicCalendarViewSet(viewsets.ModelViewSet):
    permission_classes = [AcademicCalendarPermission]
    filterset_class = FilterForAcademicCalendarViewSet
    filter_backends = (SearchFilter, OrderingFilter, DjangoFilterBackend)
    search_fields = ["program_type", "start_year", "end_year"]
    queryset = AcademicCalendar.objects.filter(is_archived=False)
    ordering_fields = ["-created_at", "start_year", "end_year"]
    http_method_names = ["options", "head", "get", "patch", "post", "delete"]

    def get_serializer_class(self):
        if self.request.method == "GET":
            return (
                AcademicCalendarListSerializer
                if self.action == "list"
                else AcademicCalendarRetrieveSerializer
            )
        if self.request.method == "POST":
            return AcademicCalendarCreateSerializer
        if self.request.method == "PATCH":
            return AcademicCalendarPatchSerializer
        return AcademicCalendarRetrieveSerializer

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        set_binary_files_null_if_empty(["file"], request.data)
        return super().create(request, *args, **kwargs)

    @transaction.atomic
    def update(self, request, *args, **kwargs):
        set_binary_files_null_if_empty(["file"], request.data)
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            instance.file.delete(save=False)
        except Exception:
            return Response(
                {"message": ACADEMIC_CALENDER_NOT_FOUND},
                status=status.HTTP_404_NOT_FOUND,
            )

        instance.delete()
        return Response(
            {"message": ACADEMIC_CALENDER_DELETED_SUCCESS},
            status=status.HTTP_200_OK,
        )


class CampusEventViewSet(viewsets.ModelViewSet):
    permission_classes = [CampusEventPermission]
    queryset = CampusEvent.objects.filter(is_archived=False)
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ["event_type", "is_active"]
    search_fields = ["title", "description_short", "description_detailed"]
    ordering_fields = ["event_start_date", "created_at"]
    ordering = ["-created_at"]
    http_method_names = ["get", "post", "patch", "delete", "head", "options"]

    def get_serializer_class(self):
        if self.request.method == "GET":
            return (
                CampusEventListSerializer
                if self.action == "list"
                else CampusEventRetrieveSerializer
            )
        if self.request.method == "POST":
            return CampusEventCreateSerializer
        if self.request.method == "PATCH":
            return CampusEventPatchSerializer
        return CampusEventRetrieveSerializer

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        set_binary_files_null_if_empty(["thumbnail"], request.data)
        return super().create(request, *args, **kwargs)

    @transaction.atomic
    def update(self, request, *args, **kwargs):
        set_binary_files_null_if_empty(["thumbnail"], request.data)
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            instance.file.delete(save=False)
        except Exception:
            return Response(
                {"message": CAMPUS_EVENT_NOT_FOUND},
                status=status.HTTP_404_NOT_FOUND,
            )

        instance.delete()
        return Response(
            {"message": CAMPUS_EVENT_DELETED_SUCCESS},
            status=status.HTTP_200_OK,
        )


class CampusEventGalleryDestroyAPIView(generics.DestroyAPIView):
    permission_classes = [CampusEventPermission]
    lookup_url_kwarg = "gallery_id"
    queryset = CampusEventGallery.objects.all()

    def get_object(self):
        obj = self.queryset.filter(
            event_id=self.kwargs["event_id"],
            pk=self.kwargs[self.lookup_url_kwarg],
        ).first()
        if not obj:
            raise NotFound({"message": EVENT_GALLERY_NOT_FOUND})
        return obj

    def delete(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.image.delete(save=False)
        instance.delete()
        return Response(
            {"message": EVENT_GALLERY_DELETED_SUCCESS},
            status=status.HTTP_200_OK,
        )


class CampusUnionViewSet(viewsets.ModelViewSet):
    permission_classes = [CampusUnionPermission]
    queryset = CampusUnion.objects.filter(is_archived=False)
    filter_backends = (SearchFilter, OrderingFilter, DjangoFilterBackend)
    filterset_fields = ["is_active"]
    search_fields = ["name"]
    ordering_fields = ["-created_at", "name"]
    http_method_names = ["get", "head", "options", "post", "patch", "delete"]

    def get_serializer_class(self):
        if self.request.method == "GET":
            return (
                CampusUnionListSerializer
                if self.action == "list"
                else CampusUnionRetrieveSerializer
            )
        if self.request.method == "POST":
            return CampusUnionCreateSerializer
        if self.request.method == "PATCH":
            return CampusUnionPatchSerializer
        return CampusUnionRetrieveSerializer

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @transaction.atomic
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @transaction.atomic
    def destroy(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
        except Exception:
            return Response(
                {"message": CAMPUS_UNION_NOT_FOUND},
                status=status.HTTP_404_NOT_FOUND,
            )
        members = instance.members.all()

        # Delete associated photo files from disk
        for member in members:
            member.photo.delete(save=False)
            member.delete()

        instance.delete()

        return Response(
            {"detail": CAMPUS_UNION_DELETED_SUCCESS},
            status=status.HTTP_200_OK,
        )

    @action(
        detail=True,
        methods=["delete"],
        url_path="member/(?P<member_id>[^/.]+)",
        name="Delete Union Member",
    )
    def delete_member(self, request, pk=None, member_id=None):
        try:
            union = self.get_object()
        except Exception:
            return Response(
                {"message": CAMPUS_UNION_NOT_FOUND},
                status=status.HTTP_404_NOT_FOUND,
            )

        try:
            member = union.members.get(pk=member_id, union=pk)
        except CampusUnionMember.DoesNotExist:
            return Response(
                {"detail": MEMBER_NOT_FOUND},
                status=status.HTTP_404_NOT_FOUND,
            )

        if member.photo:
            member.photo.delete(save=False)

        member.delete()

        return Response(
            {"detail": MEMBER_DELETED_SUCCESS},
            status=status.HTTP_200_OK,
        )


class StudentClubViewSet(viewsets.ModelViewSet):
    permission_classes = [CampusClubPermission]
    queryset = StudentClub.objects.filter(is_archived=False)
    filter_backends = (SearchFilter, OrderingFilter, DjangoFilterBackend)
    filterset_fields = ["is_active"]
    search_fields = ["name"]
    ordering_fields = ["-created_at", "name"]
    http_method_names = ["get", "head", "options", "post", "patch", "delete"]

    def get_serializer_class(self):
        if self.request.method == "GET":
            return (
                StudentClubListSerializer
                if self.action == "list"
                else StudentClubRetrieveSerializer
            )
        if self.request.method == "POST":
            return StudentClubCreateSerializer
        if self.request.method == "PATCH":
            return StudentClubPatchSerializer
        return StudentClubRetrieveSerializer

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @transaction.atomic
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @transaction.atomic
    def destroy(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
        except Exception:
            return Response(
                {"message": CAMPUS_CLUB_NOT_FOUND},
                status=status.HTTP_404_NOT_FOUND,
            )
        members = instance.members.all()

        # Delete associated photo files from disk
        for member in members:
            member.photo.delete(save=False)
            member.delete()

        instance.delete()

        return Response(
            {"detail": CAMPUS_CLUB_DELETED_SUCCESS},
            status=status.HTTP_200_OK,
        )

    @action(
        detail=True,
        methods=["delete"],
        url_path="member/(?P<member_id>[^/.]+)",
        name="Delete Club Member",
    )
    def delete_member(self, request, pk=None, member_id=None):
        try:
            club = self.get_object()
        except Exception:
            return Response(
                {"message": CAMPUS_CLUB_NOT_FOUND},
                status=status.HTTP_404_NOT_FOUND,
            )

        try:
            member = club.members.get(pk=member_id, club=pk)
        except StudentClubMember.DoesNotExist:
            return Response(
                {"detail": MEMBER_NOT_FOUND},
                status=status.HTTP_404_NOT_FOUND,
            )

        if member.photo:
            member.photo.delete(save=False)

        member.delete()

        return Response(
            {"detail": MEMBER_DELETED_SUCCESS},
            status=status.HTTP_200_OK,
        )

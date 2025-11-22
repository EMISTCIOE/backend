import django_filters
from django.db import transaction
from django.db.models import Q
from django_filters.filterset import FilterSet
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema
from rest_framework import generics, status, viewsets
from rest_framework.decorators import action
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ReadOnlyModelViewSet

# Project Imports
from src.libs.send_mail import send_campus_feedback_reply
from src.libs.utils import set_binary_files_null_if_empty
from src.user.constants import ADMIN_ROLE, EMIS_STAFF_ROLE, CAMPUS_SECTION_ROLE, CAMPUS_UNIT_ROLE
from src.user.models import User
from src.website.messages import (
    ACADEMIC_CALENDER_DELETED_SUCCESS,
    ACADEMIC_CALENDER_NOT_FOUND,
    CAMPUS_CLUB_DELETED_SUCCESS,
    CAMPUS_CLUB_NOT_FOUND,
    CAMPUS_DOWNLOAD_DELETED_SUCCESS,
    CAMPUS_DOWNLOAD_NOT_FOUND,
    CAMPUS_FEEDBACK_RESOLVE_SUCCESS,
    CAMPUS_INFO_NOT_FOUND,
    CAMPUS_REPORT_DELETED_SUCCESS,
    CAMPUS_REPORT_NOT_FOUND,
    CAMPUS_SECTION_DELETED_SUCCESS,
    CAMPUS_SECTION_NOT_FOUND,
    CAMPUS_UNION_DELETED_SUCCESS,
    CAMPUS_UNION_NOT_FOUND,
    CAMPUS_UNIT_DELETED_SUCCESS,
    CAMPUS_UNIT_NOT_FOUND,
    GLOBAL_EVENT_CREATED_SUCCESS,
    GLOBAL_EVENT_DELETED_SUCCESS,
    GLOBAL_EVENT_UPDATED_SUCCESS,
    GLOBAL_GALLERY_IMAGE_CREATED_SUCCESS,
    GLOBAL_GALLERY_IMAGE_DELETED_SUCCESS,
    GLOBAL_GALLERY_IMAGE_UPDATED_SUCCESS,
    MEMBER_DELETED_SUCCESS,
    MEMBER_NOT_FOUND,
    RESEARCH_FACILITY_DELETED_SUCCESS,
    RESEARCH_FACILITY_NOT_FOUND,
    SOCIAL_MEDIA_DELETED_SUCCESS,
    SOCIAL_MEDIA_NOT_FOUND,
)
from src.website.utils import build_global_gallery_items

from .models import (
    AcademicCalendar,
    CampusDownload,
    CampusFeedback,
    CampusInfo,
    CampusKeyOfficial,
    CampusReport,
    CampusSection,
    CampusStaffDesignation,
    CampusUnion,
    CampusUnionMember,
    CampusUnit,
    GlobalEvent,
    GlobalGalleryImage,
    ResearchFacility,
    SocialMediaLink,
    StudentClub,
    StudentClubMember,
)
from .permissions import (
    AcademicCalendarPermission,
    CampusDownloadPermission,
    CampusFeedbackPermission,
    CampusInfoPermission,
    CampusKeyOfficialPermission,
    CampusReportPermission,
    CampusSectionPermission,
    CampusUnionPermission,
    CampusUnitPermission,
    GlobalEventPermission,
    GlobalGalleryImagePermission,
    GlobalGalleryPermission,
    ResearchFacilityPermission,
    StudentClubPermission,
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
    CampusSectionCreateSerializer,
    CampusSectionListSerializer,
    CampusSectionPatchSerializer,
    CampusSectionRetrieveSerializer,
    CampusStaffDesignationSerializer,
    CampusUnionCreateSerializer,
    CampusUnionListSerializer,
    CampusUnionPatchSerializer,
    CampusUnionRetrieveSerializer,
    CampusUnitCreateSerializer,
    CampusUnitListSerializer,
    CampusUnitPatchSerializer,
    CampusUnitRetrieveSerializer,
    GlobalEventCreateSerializer,
    GlobalEventListSerializer,
    GlobalEventPatchSerializer,
    GlobalEventRetrieveSerializer,
    GlobalGalleryImageCreateSerializer,
    GlobalGalleryImageSerializer,
    GlobalGalleryImageUpdateSerializer,
    GlobalGallerySerializer,
    ResearchFacilityCreateSerializer,
    ResearchFacilityListSerializer,
    ResearchFacilityPatchSerializer,
    ResearchFacilityRetrieveSerializer,
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


class CampusKeyOfficialFilterSet(FilterSet):
    designation = django_filters.CharFilter(
        field_name="designation__code",
        lookup_expr="iexact",
    )
    is_key_official = django_filters.BooleanFilter()
    is_active = django_filters.BooleanFilter()

    class Meta:
        model = CampusKeyOfficial
        fields = ["designation", "is_key_official", "is_active"]


class CampusKeyOfficialViewSet(viewsets.ModelViewSet):
    """Campus Staff CRUD APIs"""

    permission_classes = [CampusKeyOfficialPermission]
    queryset = CampusKeyOfficial.objects.filter(is_archived=False).select_related(
        "designation",
        "department",
        "program",
        "unit",
    )
    filter_backends = [SearchFilter, OrderingFilter, DjangoFilterBackend]
    search_fields = [
        "full_name",
        "designation__title",
        "designation__code",
        "email",
        "department__name",
        "unit__name",
    ]
    ordering_fields = ["full_name", "created_at", "display_order"]
    ordering = ["display_order", "-created_at"]
    filterset_class = CampusKeyOfficialFilterSet
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


class CampusStaffDesignationViewSet(ReadOnlyModelViewSet):
    """Read-only viewset for listing available staff designations."""

    permission_classes = [CampusKeyOfficialPermission]
    serializer_class = CampusStaffDesignationSerializer
    queryset = CampusStaffDesignation.objects.filter(is_archived=False)
    filter_backends = [SearchFilter, OrderingFilter, DjangoFilterBackend]
    search_fields = ["title", "code"]
    ordering = ["title"]
    ordering_fields = ["title", "code"]
    filterset_fields = ["is_active"]
    http_method_names = ["get", "head", "options"]


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
            context={"request": request},
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        # Send a reply email to the submitter if available
        if instance.email and serializer.validated_data.get("is_resolved"):
            response_message = serializer.validated_data.get(
                "response_message",
                getattr(instance, "response_message", ""),
            )
            resolved_by = getattr(request.user, "get_full_name", lambda: None)() or getattr(
                request.user,
                "username",
                None,
            )
            send_campus_feedback_reply(
                full_name=instance.full_name,
                recipient_email=instance.email,
                response_message=response_message,
                original_message=instance.message,
                resolved_by=resolved_by,
            )
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
                {"detail": CAMPUS_DOWNLOAD_NOT_FOUND},
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
                {"detail": CAMPUS_REPORT_NOT_FOUND},
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
                {"detail": ACADEMIC_CALENDER_NOT_FOUND},
                status=status.HTTP_404_NOT_FOUND,
            )

        instance.delete()
        return Response(
            {"message": ACADEMIC_CALENDER_DELETED_SUCCESS},
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

    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user
        if getattr(user, "role", None) == "UNION":
            union_id = getattr(user, "union_id", None)
            if union_id:
                return queryset.filter(pk=union_id)
            return queryset.none()
        return queryset

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
        set_binary_files_null_if_empty(["thumbnail"], request.data)
        return super().create(request, *args, **kwargs)

    @transaction.atomic
    def update(self, request, *args, **kwargs):
        set_binary_files_null_if_empty(["thumbnail"], request.data)
        return super().update(request, *args, **kwargs)

    @transaction.atomic
    def destroy(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            if instance.thumbnail:
                instance.thumbnail.delete(save=False)
        except Exception:
            return Response(
                {"detail": CAMPUS_UNION_NOT_FOUND},
                status=status.HTTP_404_NOT_FOUND,
            )
        members = instance.members.all()

        # Delete associated photo files from disk
        for member in members:
            member.photo.delete(save=False)
            member.delete()

        instance.delete()

        return Response(
            {"message": CAMPUS_UNION_DELETED_SUCCESS},
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
                {"detail": CAMPUS_UNION_NOT_FOUND},
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
            {"message": MEMBER_DELETED_SUCCESS},
            status=status.HTTP_200_OK,
        )


class FilterForCampusSectionViewSet(FilterSet):
    class Meta:
        model = CampusSection
        fields = ["is_active", "slug"]


class CampusSectionViewSet(viewsets.ModelViewSet):
    permission_classes = [CampusSectionPermission]
    queryset = CampusSection.objects.filter(is_archived=False)
    filterset_class = FilterForCampusSectionViewSet
    filter_backends = (SearchFilter, OrderingFilter, DjangoFilterBackend)
    search_fields = ["name", "short_description", "detailed_description"]
    ordering_fields = ["display_order", "name", "created_at"]
    http_method_names = ["get", "head", "options", "post", "patch", "delete"]

    def get_serializer_class(self):
        if self.request.method == "GET":
            return (
                CampusSectionListSerializer
                if self.action == "list"
                else CampusSectionRetrieveSerializer
            )
        if self.request.method == "POST":
            return CampusSectionCreateSerializer
        if self.request.method == "PATCH":
            return CampusSectionPatchSerializer
        return CampusSectionRetrieveSerializer

    def get_queryset(self):
        qs = CampusSection.objects.filter(is_archived=False)
        user = self.request.user
        if not user or not user.is_authenticated:
            return qs.none()
        if user.is_superuser or getattr(user, "role", None) in {ADMIN_ROLE, EMIS_STAFF_ROLE}:
            return qs
        if getattr(user, "role", None) == CAMPUS_SECTION_ROLE and getattr(user, "campus_section_id", None):
            return qs.filter(id=user.campus_section_id)
        return qs.none()

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        set_binary_files_null_if_empty(["thumbnail", "hero_image"], request.data)
        return super().create(request, *args, **kwargs)

    @transaction.atomic
    def update(self, request, *args, **kwargs):
        set_binary_files_null_if_empty(["thumbnail", "hero_image"], request.data)
        return super().update(request, *args, **kwargs)

    @transaction.atomic
    def destroy(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
        except Exception:
            return Response(
                {"detail": CAMPUS_SECTION_NOT_FOUND},
                status=status.HTTP_404_NOT_FOUND,
            )

        if instance.thumbnail:
            instance.thumbnail.delete(save=False)
        if instance.hero_image:
            instance.hero_image.delete(save=False)

        if hasattr(instance, "members"):
            instance.members.clear()
        instance.delete()
        return Response(
            {"message": CAMPUS_SECTION_DELETED_SUCCESS},
            status=status.HTTP_200_OK,
        )


class FilterForCampusUnitViewSet(FilterSet):
    class Meta:
        model = CampusUnit
        fields = ["is_active", "slug"]


class CampusUnitViewSet(viewsets.ModelViewSet):
    permission_classes = [CampusUnitPermission]
    queryset = CampusUnit.objects.filter(is_archived=False)
    filterset_class = FilterForCampusUnitViewSet
    filter_backends = (SearchFilter, OrderingFilter, DjangoFilterBackend)
    search_fields = ["name", "short_description", "detailed_description"]
    ordering_fields = ["display_order", "name", "created_at"]
    http_method_names = ["get", "head", "options", "post", "patch", "delete"]

    def get_serializer_class(self):
        if self.request.method == "GET":
            return (
                CampusUnitListSerializer
                if self.action == "list"
                else CampusUnitRetrieveSerializer
            )
        if self.request.method == "POST":
            return CampusUnitCreateSerializer
        if self.request.method == "PATCH":
            return CampusUnitPatchSerializer
        return CampusUnitRetrieveSerializer

    def get_queryset(self):
        qs = CampusUnit.objects.filter(is_archived=False)
        user = self.request.user
        if not user or not user.is_authenticated:
            return qs.none()
        if user.is_superuser or getattr(user, "role", None) in {ADMIN_ROLE, EMIS_STAFF_ROLE}:
            return qs
        if getattr(user, "role", None) == CAMPUS_UNIT_ROLE and getattr(user, "campus_unit_id", None):
            return qs.filter(id=user.campus_unit_id)
        return qs.none()

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        set_binary_files_null_if_empty(["thumbnail", "hero_image"], request.data)
        return super().create(request, *args, **kwargs)

    @transaction.atomic
    def update(self, request, *args, **kwargs):
        set_binary_files_null_if_empty(["thumbnail", "hero_image"], request.data)
        return super().update(request, *args, **kwargs)

    @transaction.atomic
    def destroy(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
        except Exception:
            return Response(
                {"detail": CAMPUS_UNIT_NOT_FOUND},
                status=status.HTTP_404_NOT_FOUND,
            )

        if instance.thumbnail:
            instance.thumbnail.delete(save=False)
        if instance.hero_image:
            instance.hero_image.delete(save=False)

        if hasattr(instance, "members"):
            instance.members.clear()
        instance.delete()
        return Response(
            {"message": CAMPUS_UNIT_DELETED_SUCCESS},
            status=status.HTTP_200_OK,
        )


class FilterForResearchFacilityViewSet(FilterSet):
    class Meta:
        model = ResearchFacility
        fields = ["is_active", "slug"]


class ResearchFacilityViewSet(viewsets.ModelViewSet):
    permission_classes = [ResearchFacilityPermission]
    queryset = ResearchFacility.objects.filter(is_archived=False)
    filterset_class = FilterForResearchFacilityViewSet
    filter_backends = (SearchFilter, OrderingFilter, DjangoFilterBackend)
    search_fields = ["name", "short_description", "description", "objectives"]
    ordering_fields = ["display_order", "name", "created_at"]
    http_method_names = ["get", "head", "options", "post", "patch", "delete"]

    def get_serializer_class(self):
        if self.request.method == "GET":
            return (
                ResearchFacilityListSerializer
                if self.action == "list"
                else ResearchFacilityRetrieveSerializer
            )
        if self.request.method == "POST":
            return ResearchFacilityCreateSerializer
        if self.request.method == "PATCH":
            return ResearchFacilityPatchSerializer
        return ResearchFacilityRetrieveSerializer

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        set_binary_files_null_if_empty(["thumbnail"], request.data)
        return super().create(request, *args, **kwargs)

    @transaction.atomic
    def update(self, request, *args, **kwargs):
        set_binary_files_null_if_empty(["thumbnail"], request.data)
        return super().update(request, *args, **kwargs)

    @transaction.atomic
    def destroy(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
        except Exception:
            return Response(
                {"detail": RESEARCH_FACILITY_NOT_FOUND},
                status=status.HTTP_404_NOT_FOUND,
            )

        if instance.thumbnail:
            instance.thumbnail.delete(save=False)

        instance.delete()
        return Response(
            {"message": RESEARCH_FACILITY_DELETED_SUCCESS},
            status=status.HTTP_200_OK,
        )


class StudentClubViewSet(viewsets.ModelViewSet):
    permission_classes = [StudentClubPermission]
    queryset = StudentClub.objects.filter(is_archived=False)
    filter_backends = (SearchFilter, OrderingFilter, DjangoFilterBackend)
    filterset_fields = ["is_active"]
    search_fields = ["name"]
    ordering_fields = ["-created_at", "name"]
    http_method_names = ["get", "head", "options", "post", "patch", "delete"]

    def get_queryset(self):
        queryset = StudentClub.objects.filter(is_archived=False)
        user = self.request.user

        if getattr(user, "role", None) == User.RoleType.CLUB:
            club_id = getattr(user, "club_id", None)
            return queryset.filter(id=club_id) if club_id else queryset.none()

        if getattr(user, "role", None) == User.RoleType.DEPARTMENT_ADMIN:
            department_id = getattr(user, "department_id", None)
            if department_id:
                return queryset.filter(department_id=department_id)
            return queryset.none()

        return queryset

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
            if instance:
                instance.thumbnail.delete(save=False)
        except Exception:
            return Response(
                {"detail": CAMPUS_CLUB_NOT_FOUND},
                status=status.HTTP_404_NOT_FOUND,
            )
        members = instance.members.all()

        # Delete associated photo files from disk
        for member in members:
            member.photo.delete(save=False)
            member.delete()

        instance.delete()

        return Response(
            {"message": CAMPUS_CLUB_DELETED_SUCCESS},
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
                {"detail": CAMPUS_CLUB_NOT_FOUND},
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
            {"message": MEMBER_DELETED_SUCCESS},
            status=status.HTTP_200_OK,
        )


class GlobalGalleryImageViewSet(viewsets.ModelViewSet):
    permission_classes = [GlobalGalleryImagePermission]
    queryset = (
        GlobalGalleryImage.objects.select_related(
            "union",
            "club",
            "department",
            "global_event",
        )
        .filter(is_archived=False)
        .order_by("-created_at")
    )
    filter_backends = (SearchFilter, OrderingFilter, DjangoFilterBackend)
    filterset_fields = ["is_active", "source_type"]
    search_fields = ["caption", "source_title", "source_context"]
    ordering_fields = ["created_at", "display_order"]
    http_method_names = ["get", "post", "patch", "delete"]

    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user
        if getattr(user, "role", None) == "UNION":
            union_id = getattr(user, "union_id", None)
            if not union_id:
                return queryset.none()
            return queryset.filter(
                Q(union_id=union_id)
                | Q(global_event__unions__id=union_id),
            ).distinct()
        return queryset

    def get_serializer_class(self):
        if self.action in ["list", "retrieve"]:
            return GlobalGalleryImageSerializer
        if self.action == "create":
            return GlobalGalleryImageCreateSerializer
        return GlobalGalleryImageUpdateSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(
            data=request.data,
            context={"request": request},
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            {"message": GLOBAL_GALLERY_IMAGE_CREATED_SUCCESS},
            status=status.HTTP_201_CREATED,
        )

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(
            instance,
            data=request.data,
            partial=kwargs.get("partial", False),
            context={"request": request},
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            {"message": GLOBAL_GALLERY_IMAGE_UPDATED_SUCCESS},
            status=status.HTTP_200_OK,
        )

    def partial_update(self, request, *args, **kwargs):
        kwargs["partial"] = True
        return self.update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.image:
            instance.image.delete(save=False)
        instance.delete()
        return Response(
            {"message": GLOBAL_GALLERY_IMAGE_DELETED_SUCCESS},
            status=status.HTTP_200_OK,
        )


class FilterForGlobalEventViewSet(FilterSet):
    union = django_filters.UUIDFilter(field_name="unions__uuid")
    club = django_filters.UUIDFilter(field_name="clubs__uuid")
    department = django_filters.UUIDFilter(field_name="departments__uuid")

    class Meta:
        model = GlobalEvent
        fields = ["is_active", "event_type", "unions", "clubs", "departments"]


class GlobalEventViewSet(viewsets.ModelViewSet):
    permission_classes = [GlobalEventPermission]
    queryset = GlobalEvent.objects.filter(is_archived=False)
    filter_backends = (SearchFilter, OrderingFilter, DjangoFilterBackend)
    filterset_class = FilterForGlobalEventViewSet
    ordering_fields = ["event_start_date", "-created_at", "title"]
    http_method_names = ["get", "post", "patch", "delete"]

    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user
        if getattr(user, "role", None) == "UNION":
            union_id = getattr(user, "union_id", None)
            if union_id:
                return queryset.filter(unions__id=union_id).distinct()
            return queryset.none()
        if getattr(user, "role", None) == user.RoleType.DEPARTMENT_ADMIN:
            dept_id = getattr(user, "department_id", None)
            if dept_id:
                return queryset.filter(
                    Q(departments__id=dept_id) | Q(clubs__department_id=dept_id)
                ).distinct()
            return queryset.none()
        if getattr(user, "role", None) == user.RoleType.CLUB:
            club_id = getattr(user, "club_id", None)
            if club_id:
                return queryset.filter(clubs__id=club_id).distinct()
            return queryset.none()
        return queryset

    def get_serializer_class(self):
        if self.action in ["list", "retrieve"]:
            return (
                GlobalEventListSerializer
                if self.action == "list"
                else GlobalEventRetrieveSerializer
            )
        if self.action == "create":
            return GlobalEventCreateSerializer
        return GlobalEventPatchSerializer

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        set_binary_files_null_if_empty(["thumbnail"], request.data)
        serializer = self.get_serializer(
            data=request.data,
            context={"request": request},
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            {"message": GLOBAL_EVENT_CREATED_SUCCESS},
            status=status.HTTP_201_CREATED,
        )

    @transaction.atomic
    def update(self, request, *args, **kwargs):
        set_binary_files_null_if_empty(["thumbnail"], request.data)
        instance = self.get_object()
        serializer = self.get_serializer(
            instance,
            data=request.data,
            partial=kwargs.get("partial", False),
            context={"request": request},
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            {"message": GLOBAL_EVENT_UPDATED_SUCCESS},
            status=status.HTTP_200_OK,
        )

    @transaction.atomic
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.thumbnail:
            instance.thumbnail.delete(save=False)
        instance.delete()
        return Response(
            {"message": GLOBAL_EVENT_DELETED_SUCCESS},
            status=status.HTTP_200_OK,
        )


class GlobalGalleryPagination(LimitOffsetPagination):
    default_limit = 24
    max_limit = 120


class GlobalGalleryListAPIView(generics.GenericAPIView):
    serializer_class = GlobalGallerySerializer
    permission_classes = [GlobalGalleryPermission]
    pagination_class = GlobalGalleryPagination

    def get(self, request, *args, **kwargs):
        items = build_global_gallery_items()
        source_type = request.query_params.get("source_type")
        if source_type:
            items = [item for item in items if item["source_type"] == source_type]
        source_identifier = request.query_params.get("source_identifier")
        if source_identifier:
            items = [
                item for item in items if item["source_identifier"] == source_identifier
            ]

        search = request.query_params.get("search", "")
        if search:
            search_lower = search.lower()
            items = [
                item
                for item in items
                if search_lower in (item.get("source_name") or "").lower()
                or search_lower in (item.get("caption") or "").lower()
                or search_lower in (item.get("source_context") or "").lower()
            ]

        items.sort(key=lambda item: item["created_at"], reverse=True)
        page = self.paginate_queryset(items, request, view=self)
        serializer = self.get_serializer(page, many=True)
        return self.get_paginated_response(serializer.data)

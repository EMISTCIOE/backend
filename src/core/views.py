from django.core.exceptions import FieldDoesNotExist
from django.utils.translation import gettext as _
from django.db.models import Count
from django.utils import timezone
from datetime import timedelta
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.viewsets import ModelViewSet
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

# Project Imports
from .models import EmailConfig, DashboardStats
from .permissions import EmailConfigPermission
from .serializers import (
    EmailConfigCreateSerializer,
    EmailConfigListSerializer,
    EmailConfigPatchSerializer,
    EmailConfigRetrieveSerializer,
    DashboardStatsSerializer,
)


class EmailConfigViewSet(ModelViewSet):
    """Email Config ViewSet"""

    permission_classes = [EmailConfigPermission]
    queryset = EmailConfig.objects.filter(is_archived=False)
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    serializer_class = EmailConfigListSerializer
    filterset_fields = ["email_type"]
    search_fields = ["email_type", "default_from_email"]
    ordering = ["-created_at"]
    ordering_fields = ["id", "created_at"]
    http_method_names = ["get", "head", "options", "post", "patch"]

    def get_serializer_class(self):
        serializer_class = EmailConfigListSerializer
        if self.request.method == "GET":
            if self.action == "list":
                serializer_class = EmailConfigListSerializer
            else:
                serializer_class = EmailConfigRetrieveSerializer
        if self.request.method == "POST":
            serializer_class = EmailConfigCreateSerializer
        if self.request.method == "PATCH":
            serializer_class = EmailConfigPatchSerializer

        return serializer_class


class DashboardStatsView(APIView):
    """
    API View to get dashboard statistics.
    Calculates stats from all models and caches the result for performance.
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """
        Get dashboard statistics.
        Returns cached data if available and recent (< 30 minutes old),
        otherwise calculates fresh stats.
        """
        # Check if we have valid cached data
        force_refresh = request.query_params.get('refresh', 'false').lower() == 'true'
        
        if not force_refresh and DashboardStats.is_cache_valid(max_age_minutes=30):
            stats = DashboardStats.get_latest()
            serializer = DashboardStatsSerializer(stats)
            return Response({
                'status': 'success',
                'cached': True,
                'data': serializer.data
            })
        
        # Calculate fresh statistics
        try:
            stats_data = self._calculate_stats()
            
            # Save to database for caching
            stats_instance = DashboardStats.objects.create(**stats_data)
            
            # Serialize and return
            serializer = DashboardStatsSerializer(stats_instance)
            return Response({
                'status': 'success',
                'cached': False,
                'data': serializer.data
            })
        
        except Exception as e:
            return Response({
                'status': 'error',
                'message': f'Failed to calculate statistics: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def _calculate_stats(self):
        """Calculate all dashboard statistics"""
        from src.user.models import User
        from src.department.models import Department
        from src.notice.models import Notice
        from src.project.models import Project
        from src.research.models import Research
        from src.journal.models import Article, Author, BoardMember
        from src.curriculum.models import Subject, Routine, Suggestion
        from src.website.models import CampusFeedback
        
        now = timezone.now()
        thirty_days_ago = now - timedelta(days=30)
        seven_days_ago = now - timedelta(days=7)
        start_of_year = now.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
        
        # ===== USER STATISTICS =====
        user_qs = self._active_queryset(User)
        total_users = user_qs.count()
        active_users = user_qs.filter(last_login__gte=thirty_days_ago).count()
        new_users_this_month = user_qs.filter(
            date_joined__month=now.month,
            date_joined__year=now.year
        ).count()
        
        users_by_role = {}
        role_counts = user_qs.values('roles__name').annotate(count=Count('id'))
        for item in role_counts:
            if item['roles__name']:
                users_by_role[item['roles__name']] = item['count']
        
        # ===== DEPARTMENT STATISTICS =====
        department_qs = self._active_queryset(Department)
        total_departments = department_qs.count()
        active_departments = department_qs.filter(is_active=True).count()
        
        # ===== NOTICE STATISTICS =====
        notice_qs = self._active_queryset(Notice)
        total_notices = notice_qs.count()
        active_notices = notice_qs.filter(status='published').count()
        draft_notices = notice_qs.filter(status='draft').count()
        featured_notices = notice_qs.filter(is_featured=True).count()
        recent_notices_count = notice_qs.filter(
            created_at__gte=seven_days_ago
        ).count()
        
        notices_by_category = {}
        category_counts = notice_qs.values('category__name').annotate(count=Count('id'))
        for item in category_counts:
            if item['category__name']:
                notices_by_category[item['category__name']] = item['count']
        
        # ===== PROJECT STATISTICS =====
        project_qs = self._active_queryset(Project)
        total_projects = project_qs.count()
        
        projects_by_status = {}
        status_counts = project_qs.values('status').annotate(count=Count('id'))
        for item in status_counts:
            projects_by_status[item['status']] = item['count']
        
        projects_by_type = {}
        type_counts = project_qs.values('project_type').annotate(count=Count('id'))
        for item in type_counts:
            projects_by_type[item['project_type']] = item['count']
        
        projects_by_department = {}
        dept_counts = project_qs.values('department__name').annotate(count=Count('id'))
        for item in dept_counts:
            if item['department__name']:
                projects_by_department[item['department__name']] = item['count']
        
        completed_projects_this_year = project_qs.filter(
            status='completed',
            updated_at__gte=start_of_year
        ).count()
        
        # ===== RESEARCH STATISTICS =====
        research_qs = self._active_queryset(Research)
        total_research = research_qs.count()
        
        research_by_status = {}
        research_status_counts = research_qs.values('status').annotate(count=Count('id'))
        for item in research_status_counts:
            research_by_status[item['status']] = item['count']
        
        research_by_type = {}
        research_type_counts = research_qs.values('research_type').annotate(count=Count('id'))
        for item in research_type_counts:
            research_by_type[item['research_type']] = item['count']
        
        published_research_this_year = research_qs.filter(
            status='published',
            updated_at__gte=start_of_year
        ).count()
        
        # ===== JOURNAL STATISTICS =====
        total_articles = self._active_queryset(Article).count()
        total_authors = self._active_queryset(Author).count()
        total_board_members = self._active_queryset(BoardMember).count()
        
        # ===== CURRICULUM STATISTICS =====
        total_subjects = self._active_queryset(Subject).count()
        total_routines = self._active_queryset(Routine).count()
        total_suggestions = self._active_queryset(Suggestion).count()
        
        # ===== FEEDBACK STATISTICS =====
        feedback_qs = self._active_queryset(CampusFeedback)
        total_feedback_submissions = feedback_qs.count()
        pending_feedback = feedback_qs.filter(is_resolved=False).count()
        
        # ===== PENDING/ACTION ITEMS =====
        pending_notices = draft_notices  # Already calculated above
        pending_research = research_qs.filter(status__in=['draft', 'under_review']).count()
        
        # Calculate pending events (upcoming events)
        try:
            from src.website.models import CampusEvent
            event_qs = self._active_queryset(CampusEvent)
            pending_events = event_qs.filter(
                event_start_date__gte=now.date(),
                is_active=True,
            ).count()
        except ImportError:
            pending_events = 0
        
        # Calculate pending projects (ongoing/in-progress)
        pending_projects = project_qs.filter(status__in=['ongoing', 'in_progress', 'planning']).count()
        
        # ===== GRAPH DATA - TRENDS =====
        notices_trend = self._get_monthly_trend(Notice, 6)
        users_growth = self._get_monthly_trend(User, 6)
        research_publications_trend = self._get_monthly_trend(
            research_qs.filter(status='published'),
            12
        )
        
        # Events trend
        try:
            from src.website.models import CampusEvent
            events_trend = self._get_monthly_trend(CampusEvent, 6)
        except ImportError:
            events_trend = []
        
        # Projects trend
        projects_trend = self._get_monthly_trend(Project, 6)
        
        return {
            'total_users': total_users,
            'active_users': active_users,
            'new_users_this_month': new_users_this_month,
            'users_by_role': users_by_role,
            'total_departments': total_departments,
            'active_departments': active_departments,
            'total_notices': total_notices,
            'active_notices': active_notices,
            'draft_notices': draft_notices,
            'featured_notices': featured_notices,
            'notices_by_category': notices_by_category,
            'recent_notices_count': recent_notices_count,
            'total_projects': total_projects,
            'projects_by_status': projects_by_status,
            'projects_by_type': projects_by_type,
            'projects_by_department': projects_by_department,
            'completed_projects_this_year': completed_projects_this_year,
            'total_research': total_research,
            'research_by_status': research_by_status,
            'research_by_type': research_by_type,
            'published_research_this_year': published_research_this_year,
            'total_articles': total_articles,
            'total_authors': total_authors,
            'total_board_members': total_board_members,
            'total_subjects': total_subjects,
            'total_routines': total_routines,
            'total_suggestions': total_suggestions,
            'total_feedback_submissions': total_feedback_submissions,
            'pending_feedback': pending_feedback,
            'pending_notices': pending_notices,
            'pending_research': pending_research,
            'pending_events': pending_events,
            'pending_projects': pending_projects,
            'notices_trend': notices_trend,
            'users_growth': users_growth,
            'research_publications_trend': research_publications_trend,
            'events_trend': events_trend,
            'projects_trend': projects_trend,
        }
    
    def _get_monthly_trend(self, queryset_or_model, months=6):
        """
        Calculate monthly trend data for charts.
        Returns list of {month: 'Jan', count: 10} objects
        """
        from src.user.models import User
        
        if hasattr(queryset_or_model, 'filter'):
            qs = queryset_or_model
            model_class = getattr(queryset_or_model, 'model', None)
            if model_class and self._model_has_field(model_class, 'is_archived'):
                qs = qs.filter(is_archived=False)
        else:
            model_class = queryset_or_model
            qs = self._active_queryset(model_class)

        now = timezone.now()
        trend_data = []
        
        for i in range(months - 1, -1, -1):
            month_date = now - timedelta(days=30 * i)
            month_start = month_date.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            
            if month_date.month == 12:
                month_end = month_start.replace(year=month_start.year + 1, month=1)
            else:
                month_end = month_start.replace(month=month_start.month + 1)
            
            if model_class == User:
                date_field = 'date_joined'
            else:
                date_field = 'created_at'
            
            count = qs.filter(**{
                f'{date_field}__gte': month_start,
                f'{date_field}__lt': month_end
            }).count()
            
            trend_data.append({
                'month': month_start.strftime('%b %Y'),
                'count': count
            })
        
        return trend_data

    def _active_queryset(self, model):
        queryset = model.objects.all()
        if self._model_has_field(model, 'is_archived'):
            return queryset.filter(is_archived=False)
        return queryset

    def _model_has_field(self, model, field_name):
        try:
            model._meta.get_field(field_name)
        except FieldDoesNotExist:
            return False
        return True

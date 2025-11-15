from django.utils.translation import gettext as _
from django.db.models import Count, Q
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
        from src.notice.models import Notice, NoticeCategory
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
        total_users = User.objects.filter(is_archived=False).count()
        active_users = User.objects.filter(
            is_archived=False,
            last_login__gte=thirty_days_ago
        ).count()
        new_users_this_month = User.objects.filter(
            is_archived=False,
            date_joined__month=now.month,
            date_joined__year=now.year
        ).count()
        
        # Users by role
        users_by_role = {}
        role_counts = User.objects.filter(is_archived=False).values('role__name').annotate(count=Count('id'))
        for item in role_counts:
            if item['role__name']:
                users_by_role[item['role__name']] = item['count']
        
        # ===== DEPARTMENT STATISTICS =====
        total_departments = Department.objects.filter(is_archived=False).count()
        active_departments = Department.objects.filter(is_archived=False, is_active=True).count()
        
        # ===== NOTICE STATISTICS =====
        total_notices = Notice.objects.filter(is_archived=False).count()
        active_notices = Notice.objects.filter(is_archived=False, status='published').count()
        draft_notices = Notice.objects.filter(is_archived=False, status='draft').count()
        featured_notices = Notice.objects.filter(is_archived=False, is_featured=True).count()
        recent_notices_count = Notice.objects.filter(
            is_archived=False,
            created_at__gte=seven_days_ago
        ).count()
        
        # Notices by category
        notices_by_category = {}
        category_counts = Notice.objects.filter(is_archived=False).values('category__name').annotate(count=Count('id'))
        for item in category_counts:
            if item['category__name']:
                notices_by_category[item['category__name']] = item['count']
        
        # ===== PROJECT STATISTICS =====
        total_projects = Project.objects.filter(is_archived=False).count()
        
        # Projects by status
        projects_by_status = {}
        status_counts = Project.objects.filter(is_archived=False).values('status').annotate(count=Count('id'))
        for item in status_counts:
            projects_by_status[item['status']] = item['count']
        
        # Projects by type
        projects_by_type = {}
        type_counts = Project.objects.filter(is_archived=False).values('project_type').annotate(count=Count('id'))
        for item in type_counts:
            projects_by_type[item['project_type']] = item['count']
        
        # Projects by department
        projects_by_department = {}
        dept_counts = Project.objects.filter(is_archived=False).values('department__name').annotate(count=Count('id'))
        for item in dept_counts:
            if item['department__name']:
                projects_by_department[item['department__name']] = item['count']
        
        completed_projects_this_year = Project.objects.filter(
            is_archived=False,
            status='completed',
            updated_at__gte=start_of_year
        ).count()
        
        # ===== RESEARCH STATISTICS =====
        total_research = Research.objects.filter(is_archived=False).count()
        
        # Research by status
        research_by_status = {}
        research_status_counts = Research.objects.filter(is_archived=False).values('status').annotate(count=Count('id'))
        for item in research_status_counts:
            research_by_status[item['status']] = item['count']
        
        # Research by type
        research_by_type = {}
        research_type_counts = Research.objects.filter(is_archived=False).values('research_type').annotate(count=Count('id'))
        for item in research_type_counts:
            research_by_type[item['research_type']] = item['count']
        
        published_research_this_year = Research.objects.filter(
            is_archived=False,
            status='published',
            updated_at__gte=start_of_year
        ).count()
        
        # ===== JOURNAL STATISTICS =====
        total_articles = Article.objects.filter(is_archived=False).count()
        total_authors = Author.objects.filter(is_archived=False).count()
        total_board_members = BoardMember.objects.filter(is_archived=False).count()
        
        # ===== CURRICULUM STATISTICS =====
        total_subjects = Subject.objects.filter(is_archived=False).count()
        total_routines = Routine.objects.filter(is_archived=False).count()
        total_suggestions = Suggestion.objects.filter(is_archived=False).count()
        
        # ===== FEEDBACK STATISTICS =====
        total_feedback_submissions = CampusFeedback.objects.filter(is_archived=False).count()
        pending_feedback = CampusFeedback.objects.filter(is_archived=False, is_resolved=False).count()
        
        # ===== GRAPH DATA - TRENDS =====
        # Notices trend (last 6 months)
        notices_trend = self._get_monthly_trend(Notice, 6)
        
        # Users growth (last 6 months)
        users_growth = self._get_monthly_trend(User, 6)
        
        # Research publications trend (last 12 months)
        research_publications_trend = self._get_monthly_trend(
            Research.objects.filter(status='published'), 
            12
        )
        
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
            'notices_trend': notices_trend,
            'users_growth': users_growth,
            'research_publications_trend': research_publications_trend,
        }
    
    def _get_monthly_trend(self, queryset_or_model, months=6):
        """
        Calculate monthly trend data for charts.
        Returns list of {month: 'Jan', count: 10} objects
        """
        from src.user.models import User
        
        now = timezone.now()
        trend_data = []
        
        for i in range(months - 1, -1, -1):
            month_date = now - timedelta(days=30 * i)
            month_start = month_date.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            
            if month_date.month == 12:
                month_end = month_start.replace(year=month_start.year + 1, month=1)
            else:
                month_end = month_start.replace(month=month_start.month + 1)
            
            # Get queryset
            if hasattr(queryset_or_model, 'filter'):
                qs = queryset_or_model
            else:
                qs = queryset_or_model.objects.filter(is_archived=False)
            
            # Determine date field based on model type
            # User model uses 'date_joined' instead of 'created_at'
            if hasattr(queryset_or_model, 'model'):
                model_class = queryset_or_model.model
            else:
                model_class = queryset_or_model
            
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

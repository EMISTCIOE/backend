from django.contrib import admin
from .models import Notice, NoticeType, NoticeCategory


class NoticeAdmin(admin.ModelAdmin):
    list_display = ('title',  'notice_category', 'is_featured',
                    'published_date', 'is_active')
    list_filter = ('title', 'description', 'notice_category',
                   'department_id', 'is_featured', 'published_date', 'is_active')
    search_fields = ('title', 'description', 'category',
                     'department_id', 'is_featured', 'published_date', 'is_active')

# class NoticeInline(admin.StackedInline):
#     model = Notice
#     extra = 1


class NoticeCategoryAdmin(admin.ModelAdmin):
    # inlines = [NoticeInline]
    list_display = ['notice_type', 'category']
    search_fields = ['notice_category']


class NoticeCategoryInline(admin.StackedInline):
    model = NoticeCategory
    extra = 1


class NoticeTypeAdmin(admin.ModelAdmin):
    inlines = [NoticeCategoryInline]
    list_display = ['notice_type']


# Register your models here.
admin.site.register(Notice, NoticeAdmin)
# admin.site.register(NoticeCategory, NoticeCategoryAdmin)
admin.site.register(NoticeType, NoticeTypeAdmin)

# admin.site.register(NoticeCategory, NoticeCategoryAdmin)

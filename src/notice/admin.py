from django.contrib import admin

from .models import Notice, NoticeCategory, NoticeMedia

admin.site.register(NoticeCategory)
admin.site.register(Notice)
admin.site.register(NoticeMedia)

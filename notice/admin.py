from django.contrib import admin
from .models import Notice, NoticeType

# Register your models here.
admin.site.register(Notice)
admin.site.register(NoticeType)

from django.contrib import admin

from .models import UserRole, User, UserAccountVerification

admin.site.register(User)
admin.site.register(UserRole)
admin.site.register(UserAccountVerification)

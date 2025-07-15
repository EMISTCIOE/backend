from rest_framework import serializers

from src.user.models import UserRole


class RoleForUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserRole
        fields = ["id", "name", "codename"]

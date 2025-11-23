from rest_framework import serializers

from .models import Project, ProjectMember, ProjectTag, ProjectTagAssignment


class ProjectMemberSerializer(serializers.ModelSerializer):
    department_name = serializers.CharField(source="department.name", read_only=True)

    class Meta:
        model = ProjectMember
        fields = [
            "id",
            "full_name",
            "roll_number",
            "email",
            "phone_number",
            "department",
            "department_name",
            "role",
            "linkedin_url",
            "github_url",
        ]


class ProjectTagSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProjectTag
        fields = ["id", "name", "slug", "color"]


class ProjectListSerializer(serializers.ModelSerializer):
    department_name = serializers.CharField(source="department.name", read_only=True)
    academic_program_name = serializers.CharField(
        source="academic_program.name",
        read_only=True,
        allow_null=True,
    )
    academic_program_short_name = serializers.CharField(
        source="academic_program.short_name",
        read_only=True,
        allow_null=True,
    )
    members_count = serializers.SerializerMethodField()
    tags = serializers.SerializerMethodField()

    class Meta:
        model = Project
        fields = [
            "id",
            "slug",
            "title",
            "abstract",
            "project_type",
            "status",
            "department",
            "department_name",
            "academic_program",
            "academic_program_name",
            "academic_program_short_name",
            "supervisor_name",
            "academic_year",
            "thumbnail",
            "github_url",
            "demo_url",
            "is_featured",
            "is_published",
            "views_count",
            "members_count",
            "tags",
            "created_at",
            "updated_at",
        ]

    def get_members_count(self, obj):
        return obj.members.count()

    def get_tags(self, obj):
        tag_assignments = obj.tag_assignments.select_related("tag").all()
        return [
            {"id": ta.tag.id, "name": ta.tag.name, "color": ta.tag.color}
            for ta in tag_assignments
        ]


class ProjectDetailSerializer(serializers.ModelSerializer):
    department_name = serializers.CharField(source="department.name", read_only=True)
    academic_program_name = serializers.CharField(
        source="academic_program.name",
        read_only=True,
        allow_null=True,
    )
    academic_program_short_name = serializers.CharField(
        source="academic_program.short_name",
        read_only=True,
        allow_null=True,
    )
    members = ProjectMemberSerializer(many=True, read_only=True)
    tags = serializers.SerializerMethodField()

    class Meta:
        model = Project
        fields = [
            "id",
            "slug",
            "title",
            "description",
            "abstract",
            "project_type",
            "status",
            "department",
            "department_name",
            "academic_program",
            "academic_program_name",
            "academic_program_short_name",
            "supervisor_name",
            "supervisor_email",
            "start_date",
            "end_date",
            "academic_year",
            "github_url",
            "demo_url",
            "report_file",
            "thumbnail",
            "technologies_used",
            "is_featured",
            "is_published",
            "views_count",
            "members",
            "tags",
            "created_at",
            "updated_at",
        ]

    def get_tags(self, obj):
        tag_assignments = obj.tag_assignments.select_related("tag").all()
        return [
            {"id": ta.tag.id, "name": ta.tag.name, "color": ta.tag.color}
            for ta in tag_assignments
        ]


class ProjectCreateUpdateSerializer(serializers.ModelSerializer):
    members = ProjectMemberSerializer(many=True, required=False)
    tag_ids = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True,
        required=False,
        allow_empty=True,
    )

    def _get_request_user(self):
        request = self.context.get("request")
        if request and hasattr(request, "user"):
            return request.user
        return None

    class Meta:
        model = Project
        fields = [
            "title",
            "description",
            "abstract",
            "project_type",
            "status",
            "department",
            "academic_program",
            "supervisor_name",
            "supervisor_email",
            "start_date",
            "end_date",
            "academic_year",
            "github_url",
            "demo_url",
            "report_file",
            "thumbnail",
            "technologies_used",
            "is_featured",
            "is_published",
            "members",
            "tag_ids",
        ]

    def create(self, validated_data):
        members_data = validated_data.pop("members", [])
        tag_ids = validated_data.pop("tag_ids", [])
        request_user = self._get_request_user()
        creator = validated_data.get("created_by") or request_user
        updater = validated_data.get("updated_by") or request_user

        project = Project.objects.create(**validated_data)

        # Create members
        for member_data in members_data:
            ProjectMember.objects.create(
                project=project,
                created_by=creator,
                updated_by=updater,
                **member_data,
            )

        # Assign tags
        for tag_id in tag_ids:
            try:
                tag = ProjectTag.objects.get(id=tag_id)
                ProjectTagAssignment.objects.create(project=project, tag=tag)
            except ProjectTag.DoesNotExist:
                pass

        return project

    def update(self, instance, validated_data):
        members_data = validated_data.pop("members", None)
        tag_ids = validated_data.pop("tag_ids", None)
        request_user = self._get_request_user()
        updater = validated_data.get("updated_by") or request_user

        # Update project fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        # Update members if provided
        if members_data is not None:
            # Delete existing members
            instance.members.all().delete()
            # Create new members
            for member_data in members_data:
                ProjectMember.objects.create(
                    project=instance,
                    created_by=instance.created_by or updater,
                    updated_by=updater,
                    **member_data,
                )

        # Update tags if provided
        if tag_ids is not None:
            # Delete existing tag assignments
            instance.tag_assignments.all().delete()
            # Create new tag assignments
            for tag_id in tag_ids:
                try:
                    tag = ProjectTag.objects.get(id=tag_id)
                    ProjectTagAssignment.objects.create(project=instance, tag=tag)
                except ProjectTag.DoesNotExist:
                    pass

        return instance

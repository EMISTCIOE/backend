from rest_framework import serializers
from .models import (
    Research, ResearchParticipant, ResearchCategory, 
    ResearchCategoryAssignment, ResearchPublication
)


class ResearchParticipantSerializer(serializers.ModelSerializer):
    department_name = serializers.CharField(source='department.name', read_only=True)
    
    class Meta:
        model = ResearchParticipant
        fields = [
            'id', 'full_name', 'participant_type', 'email', 'phone_number',
            'department', 'department_name', 'designation', 'roll_number',
            'organization', 'role', 'linkedin_url', 'orcid_id', 'is_corresponding_author'
        ]


class ResearchCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ResearchCategory
        fields = ['id', 'name', 'slug', 'description', 'color']


class ResearchPublicationSerializer(serializers.ModelSerializer):
    class Meta:
        model = ResearchPublication
        fields = [
            'id', 'title', 'journal_conference', 'publication_date',
            'doi', 'url', 'citation_count'
        ]


class ResearchListSerializer(serializers.ModelSerializer):
    department_name = serializers.CharField(source='department.name', read_only=True)
    participants_count = serializers.SerializerMethodField()
    categories = serializers.SerializerMethodField()
    principal_investigator_short = serializers.SerializerMethodField()
    
    class Meta:
        model = Research
        fields = [
            'id', 'title', 'abstract', 'research_type', 'status',
            'department', 'department_name', 'principal_investigator_short',
            'funding_agency', 'funding_amount', 'start_date', 'end_date',
            'thumbnail', 'is_featured', 'is_published', 'views_count',
            'participants_count', 'categories', 'created_at', 'updated_at'
        ]
    
    def get_participants_count(self, obj):
        return obj.participants.count()
    
    def get_categories(self, obj):
        category_assignments = obj.category_assignments.select_related('category').all()
        return [{'id': ca.category.id, 'name': ca.category.name, 'color': ca.category.color} 
                for ca in category_assignments]
    
    def get_principal_investigator_short(self, obj):
        # Return first name and last initial for privacy
        parts = obj.principal_investigator.split()
        if len(parts) > 1:
            return f"{parts[0]} {parts[-1][0]}."
        return parts[0] if parts else ""


class ResearchDetailSerializer(serializers.ModelSerializer):
    department_name = serializers.CharField(source='department.name', read_only=True)
    participants = ResearchParticipantSerializer(many=True, read_only=True)
    categories = serializers.SerializerMethodField()
    publications = ResearchPublicationSerializer(many=True, read_only=True)
    
    class Meta:
        model = Research
        fields = [
            'id', 'title', 'description', 'abstract', 'research_type', 'status',
            'department', 'department_name', 'principal_investigator', 'pi_email',
            'start_date', 'end_date', 'funding_agency', 'funding_amount',
            'keywords', 'methodology', 'expected_outcomes', 'publications_url',
            'project_url', 'github_url', 'report_file', 'thumbnail',
            'is_featured', 'is_published', 'views_count', 'participants',
            'categories', 'publications', 'created_at', 'updated_at'
        ]
    
    def get_categories(self, obj):
        category_assignments = obj.category_assignments.select_related('category').all()
        return [{'id': ca.category.id, 'name': ca.category.name, 'color': ca.category.color} 
                for ca in category_assignments]


class ResearchCreateUpdateSerializer(serializers.ModelSerializer):
    participants = ResearchParticipantSerializer(many=True, required=False)
    publications = ResearchPublicationSerializer(many=True, required=False)
    category_ids = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True,
        required=False,
        allow_empty=True
    )
    
    class Meta:
        model = Research
        fields = [
            'title', 'description', 'abstract', 'research_type', 'status',
            'department', 'principal_investigator', 'pi_email',
            'start_date', 'end_date', 'funding_agency', 'funding_amount',
            'keywords', 'methodology', 'expected_outcomes', 'publications_url',
            'project_url', 'github_url', 'report_file', 'thumbnail',
            'is_featured', 'is_published', 'participants', 'publications', 'category_ids'
        ]
    
    def create(self, validated_data):
        participants_data = validated_data.pop('participants', [])
        publications_data = validated_data.pop('publications', [])
        category_ids = validated_data.pop('category_ids', [])
        
        research = Research.objects.create(**validated_data)
        
        # Create participants
        for participant_data in participants_data:
            ResearchParticipant.objects.create(research=research, **participant_data)
        
        # Create publications
        for publication_data in publications_data:
            ResearchPublication.objects.create(research=research, **publication_data)
        
        # Assign categories
        for category_id in category_ids:
            try:
                category = ResearchCategory.objects.get(id=category_id)
                ResearchCategoryAssignment.objects.create(research=research, category=category)
            except ResearchCategory.DoesNotExist:
                pass
        
        return research
    
    def update(self, instance, validated_data):
        participants_data = validated_data.pop('participants', None)
        publications_data = validated_data.pop('publications', None)
        category_ids = validated_data.pop('category_ids', None)
        
        # Update research fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        # Update participants if provided
        if participants_data is not None:
            # Delete existing participants
            instance.participants.all().delete()
            # Create new participants
            for participant_data in participants_data:
                ResearchParticipant.objects.create(research=instance, **participant_data)
        
        # Update publications if provided
        if publications_data is not None:
            # Delete existing publications
            instance.publications.all().delete()
            # Create new publications
            for publication_data in publications_data:
                ResearchPublication.objects.create(research=instance, **publication_data)
        
        # Update categories if provided
        if category_ids is not None:
            # Delete existing category assignments
            instance.category_assignments.all().delete()
            # Create new category assignments
            for category_id in category_ids:
                try:
                    category = ResearchCategory.objects.get(id=category_id)
                    ResearchCategoryAssignment.objects.create(research=instance, category=category)
                except ResearchCategory.DoesNotExist:
                    pass
        
        return instance
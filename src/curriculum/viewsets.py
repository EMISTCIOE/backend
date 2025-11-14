from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticatedOrReadOnly

from .models import Routine, Subject, Suggestion
from .serializers import RoutineSerializer, SubjectSerializer, SuggestionSerializer


class RoutineViewSet(viewsets.ModelViewSet):
    queryset = Routine.objects.all()
    serializer_class = RoutineSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]


class SubjectViewSet(viewsets.ModelViewSet):
    queryset = Subject.objects.all()
    serializer_class = SubjectSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

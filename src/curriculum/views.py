from django.http import JsonResponse
from rest_framework.decorators import api_view
from rest_framework.generics import ListAPIView
from rest_framework.parsers import JSONParser
from rest_framework.permissions import IsAuthenticatedOrReadOnly

from .models import Subject
from .serializers import SubjectSerializer, SuggestionSerializer


# Create your views here.
class DepartmentSubjects(ListAPIView):
    model = Subject
    serializer_class = SubjectSerializer
    paginate_by = 10
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        program = self.request.GET.get("program", "").lower()
        code = self.request.GET.get("code", "").lower()
        sub_name = self.request.GET.get("name", "").lower()
        queryset = Subject.objects.all()
        if program:
            queryset = queryset.filter(program__icontains=program)
        if code:
            queryset = queryset.filter(code__iexact=code)
        if sub_name:
            queryset = queryset.filter(name__icontains=sub_name)
        return queryset

    # customm view for suggestion box


@api_view(["POST"])
def suggestion_create_view(request):
    if request.method == "POST":
        data = JSONParser().parse(request)
        serializer = SuggestionSerializer(data=data)

        if serializer.is_valid():
            serializer.save()
            return JsonResponse(serializer.data, status=201)
        return JsonResponse(serializer.errors, status=400)

    return JsonResponse({"error": "Only POST requests are allowed"}, status=405)

from rest_framework import routers

from .views import EmailConfigViewSet

router = routers.DefaultRouter(trailing_slash=False)

router.register("email-configs", EmailConfigViewSet)


list_urls = []

urlpatterns = [*list_urls, *router.urls]

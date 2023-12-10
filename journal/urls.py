from django.urls import path, include
from rest_framework import routers
from .viewsets import ArticleViewsets, BoardMemberViewset
from .views import ArticleSearchView, BoardMemberSearchView, ArticleXMLPostView

router = routers.DefaultRouter()
router.register(r'articles', ArticleViewsets)
router.register(r'board-members', BoardMemberViewset)


urlpatterns = [
    path('', include(router.urls)),
    path('article-search/', ArticleSearchView.as_view(), name='article-search'),
    path('board-member-search/', BoardMemberSearchView.as_view(),
         name='board-member-search'),
    path('article-xml/', ArticleXMLPostView.as_view(), name='article-xml'),

]

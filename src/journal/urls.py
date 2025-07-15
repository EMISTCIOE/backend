from django.urls import include, path
from rest_framework import routers

from .views import ArticleSearchView, ArticleXMLPostView, BoardMemberSearchView
from .viewsets import ArticleViewsets, AuthorViewset, BoardMemberViewset

router = routers.DefaultRouter()
router.register(r"articles", ArticleViewsets)
router.register(r"board-members", BoardMemberViewset)
router.register(r"authors", AuthorViewset)


urlpatterns = [
    path("", include(router.urls)),
    path("article-search/", ArticleSearchView.as_view(), name="article-search"),
    path(
        "board-member-search/",
        BoardMemberSearchView.as_view(),
        name="board-member-search",
    ),
    path("article-xml/", ArticleXMLPostView.as_view(), name="article-xml"),
]

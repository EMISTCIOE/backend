from django.urls import path

from src.contact.views import PhoneNumberPublicListView

urlpatterns = [
    path('phone-numbers/', PhoneNumberPublicListView.as_view(), name='phonenumber-public-list'),
]
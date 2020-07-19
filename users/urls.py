# users/urls.py
from django.urls import include, path
from .views import *

urlpatterns = [
    path("accounts/signup/", UserSignupView.as_view()),
    path("accounts/customer/signup/", CustomerSignupView.as_view()),
]
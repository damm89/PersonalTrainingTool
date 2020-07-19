# pages/urls.py
from django.urls import path,include

from . import views

urlpatterns = [
    path('', views.HomePageView.as_view(), name='home'),
    path('support/',views.SupportView),
    path("accounts/email/", views.HomePageView.as_view()),
    path("pricing/",views.PricingView,name='pricing'),
]
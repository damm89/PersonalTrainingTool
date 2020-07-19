from django.urls import path
from django.conf.urls import url

from . import views

app_name = 'api'
urlpatterns = [
    path("<str:category>/<int:item_id>/delete", views.DeleteItem, name="delete"),
    path("get/view/<str:category>/", views.APIView, name="get-view"),
    path("get/<str:category>/", views.GetItemData, name="get-item"),
    path("get/search/<str:category>/", views.searchSuggestion, name="search")
]
from django.urls import path
from django.conf.urls import url

from . import views
import api.views

app_name = 'ingredients'
urlpatterns = [
    path("mass-upload", views.MassUploadIngredients, name='mass-upload'),
    path("", api.views.APIView, {'category':'ingredients'}, name='ingredients'),
    path("tags", api.views.APIView, {'category':'ingredients-tags'}, name='ingredients-tags'),
    path("tags/<int:item_id>/delete", api.views.DeleteItem, {'category':'ingredients-tags'}, name='delete-ingredients-tags'),
    path('add', views.CreateIngredient, name='create-ingredient'),
    path('upload', views.UploadIngredient, name='upload-ingredients'),
    path('<int:ingredient_id>/edit', views.EditIngredient, name='edit-ingredient'),
    path('<int:item_id>/delete', api.views.DeleteItem, {'category':'ingredients'}, name='delete-ingredient'),
]
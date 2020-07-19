from django.urls import path
from django.conf.urls import url

from . import views

import api.views

app_name = 'meals'
urlpatterns = [
    path("", api.views.APIView, {'category':'meals'}, name='meals'),
    path("categories", api.views.APIView, {'category':'meals-categories'}, name='meal-categories'),
    path("categories/<int:item_id>/delete", api.views.DeleteItem, {'category':'meals_categories'}, name='delete-meals-category'),
    path('add', views.CreateMeal, name='create-meal'),
    path('tags/add', views.CreateTagMeal, name='create-tag-meal'),
    path('<int:meal_id>/edit', views.EditMeal, name='edit-meal'),
    path('<int:item_id>/delete', api.views.DeleteItem, {'category':'meals'}, name='delete-meal'),
]
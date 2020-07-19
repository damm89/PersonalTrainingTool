from django.urls import path
from django.conf.urls import url

from . import views

import api.views

app_name = 'mealplans'
urlpatterns = [
    path("", api.views.APIView, {'category': 'mealplans'}, name='mealplans'),
    path('templates', api.views.APIView, {'category': 'mealplans-templates'}, name='mealplan-templates'),
    path('templates/add', views.CreateMealPlanTemplate, name='create-mealplan-template'),
    path('templates/<int:item_id>/edit', views.EditMealPlanTemplate, name='edit-mealplan-template'),
    path('templates/<int:item_id>/delete', api.views.DeleteItem, {'category':'mealplantemplates'}, name='delete-mealplan-template'),
    path('add', views.CreateMealPlan, name='create-mealplan'),
    path('<int:item_id>/delete', api.views.DeleteItem, {'category':'mealplans'}, name='delete-mealplan'),
    path('<int:item_id>/show', views.ShowMealPlan, name='show-mealplan'),
    path('<int:item_id>/edit', views.EditMealPlan, name='edit-mealplan'),
]
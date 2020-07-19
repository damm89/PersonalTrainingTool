from django.urls import path

from . import views

import api.views

app_name = 'clientaccounts'
urlpatterns = [
    path("", api.views.APIView, {'category':'clientaccounts'}, name='client-accounts'),
    path("add", views.CreateAccount, name='create-client-account'),
    path("<int:client_id>/edit", views.EditAccount, name='edit-client-account'),
    path("<int:item_id>/delete", api.views.DeleteItem, {'category':'clientaccounts'}, name='delete-client-account'),
]
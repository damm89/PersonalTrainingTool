"""ws URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import include, path
from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls import url

urlpatterns = [
    path('', include('pages.urls')),
    #path('', include('plans.urls')),
    path('', include('users.urls')),

    # Django Admin
    path('admin/', admin.site.urls),

    # Allauth
    path('accounts/', include('allauth.urls')),
    

    path('ingredients/', include('ingredients.urls', namespace='ingredients')),
    path('meals/', include('meals.urls', namespace='meals')),
    path('mealplans/', include('mealplans.urls', namespace='mealplans')),
    path('clientaccounts/', include('clientaccounts.urls', namespace='clientaccounts')),        
    path('dashboard/', include('dashboard.urls', namespace='dashboard')), 
    path("api/", include("api.urls", namespace="api")),
       

]+ static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

	

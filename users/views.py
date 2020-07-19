""" from django.shortcuts import render

# Create your views here.
# users/views.py
from django.urls import reverse_lazy
from django.views import generic

from .forms import CustomUserCreationForm

class SignUp(generic.CreateView):
    form_class = CustomUserCreationForm
    success_url = reverse_lazy('login')
    template_name = 'signup.html'

"""
from .mixins import ProfileSignupView
from .models import CustomUser

class UserSignupView(ProfileSignupView):
   success_url = '/profile'
   profile_class = CustomUser()
   is_user = True


class CustomerSignupView(ProfileSignupView):
    success_url = '/profile'
    profile_class = CustomUser()
    is_user = False

from django.shortcuts import render
from django.contrib.auth.decorators import login_required

from clientaccounts.models import *

@login_required
def HomeView(request):
    """
    Shows client's account data
    """
    clients_data = ClientAccount.objects.filter(email=request.user.email).all()
    return render(request, 'plans/home.html', {"clients":clients_data})


@login_required
def ProfileView(request):
    clients_data = ClientAccount.objects.filter(email=request.user.email).all()
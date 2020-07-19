from django.contrib.auth.decorators import login_required
from django.shortcuts import render

@login_required
def ProfileView(request):
    """
    If clientaccounts has accounts - show list of accounts otherwise show create-client-account.
    """
    return render(request, 'dashboard/home.html',{})
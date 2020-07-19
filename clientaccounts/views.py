from django.shortcuts import render
from django.contrib import messages
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from django.forms.models import model_to_dict
from django.http import HttpResponseRedirect
from django.urls import reverse

from .forms import *
from .models import *

from .static_variables import *
from .functions import *

from ws.static_variables import ERROR_MESSAGE, SUCCESS_MESSAGE
    

@login_required
def CreateAccount(request):
    """
    Creates an account in a clientaccounts.
    """

    if request.method == 'GET':
        form = ClientForm()
        return render(request, 'clientaccounts/create.html', {'form': form, 'purpose':'add'})

    elif request.method == "POST":
        form = ClientForm(request.POST)
        if form.is_valid():
            client_account = ClientAccount(**form.cleaned_data)
            client_account.owner = request.user
            client_account.save()
            messages.success(request, SUCCESS_MESSAGE.format("You successfully added account: {}.".format(client_account.name)),extra_tags='ilovepancakesclientaccounts')
            return HttpResponseRedirect(reverse('clientaccounts:client-accounts'))

        else:
            messages.error(request, ERROR_MESSAGE.format('Check your inputs.'),extra_tags='ilovepancakesclientaccounts')
            return render(request, 'clientaccounts/create.html', {'form': form, 'purpose':'add'})
    else:
        messages.error(request, ERROR_MESSAGE.format('Yo dawg.'),extra_tags='ilovepancakesclientaccounts')
        return HttpResponseRedirect(reverse('clientaccounts:client-accounts')) 


@login_required
def EditAccount(request,client_id):
    """
    Edits an account on a clientaccounts.
    """
    
    clientaccount = ClientAccount.objects.get(pk=client_id)

    if request.user == clientaccount.owner:
        if request.method == "GET":
            form = ClientForm(model_to_dict(clientaccount))
            return render(request, 'clientaccounts/create.html', {'form': form, 'purpose':'edit', 'client_id':client_id})

        elif request.method == "POST":
            form = ClientForm(request.POST)

            if form.is_valid():
                for k in form.cleaned_data:
                    setattr(clientaccount, k, form.cleaned_data[k])

                clientaccount.save()
                messages.success(request, SUCCESS_MESSAGE.format("You successfully edited account: {}.".format(clientaccount.name)),extra_tags='ilovepancakesclientaccounts')
                return HttpResponseRedirect(reverse('clientaccounts:client-accounts'))
            else:
                messages.error(request, ERROR_MESSAGE.format('Check your inputs.'),extra_tags='ilovepancakesclientaccounts')
                return render(request, 'clientaccounts/create.html', {'form': form, 'purpose':'edit', 'client_id':client_id})

        else:
            messages.error(request, ERROR_MESSAGE.format('Yo dawg.'),extra_tags='ilovepancakesclientaccounts')
            return render(request, 'clientaccounts/create.html', {'form': form, 'purpose':'edit', 'client_id':client_id})
    
    else:
        messages.error(request, ERROR_MESSAGE.format('You are not the owner of account: {}.'.format(clientaccount.name)),extra_tags='ilovepancakesclientaccounts')
        return HttpResponseRedirect(reverse('clientaccounts:client-accounts')) 
            
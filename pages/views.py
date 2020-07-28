from django.shortcuts import render
from django.views.generic import TemplateView
from pages.forms import SupportForm

from ws.static_variables import SUCCESS_MESSAGE, ERROR_MESSAGE

# Create your views here.

class HomePageView(TemplateView):
    template_name = 'pages/home.html'

from django.contrib import messages
from django.core.mail import send_mail, BadHeaderError
from django.http import HttpResponse
from django.shortcuts import redirect

def SupportView(request):
    if request.method== 'GET':
        form = SupportForm()
    else:
        form = SupportForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            email = form.cleaned_data['email']
            message = form.cleaned_data['message']
            
            subject = "Support Request {} {}".format(name,email)
            message = '\n\n'.join([message,email])
            
            try:
                send_mail(subject, message, 'noreply@pttool.com', ['danielammeraal@gmail.com'])
                messages.success(request, SUCCESS_MESSAGE.format("We will try to contact you within 24 hours. Thank you."), extra_tags='ilovepancakesupport')

            except Exception as e:
                messages.error(request, ERROR_MESSAGE.format("Something went wrong: {}".format(e.args[0])),extra_tags='ilovepancakesupport')

    return render(request, 'pages/support.html', {'form': form})

def PricingView(request):
    return render(request, 'pages/pricing.html')

def BuyNowView(request):
    return render(request,'pages/buy-now.html')
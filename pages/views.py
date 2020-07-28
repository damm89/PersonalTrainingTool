from django.shortcuts import render
from django.views.generic import TemplateView
from pages.forms import SupportForm

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
            except Exception as e:
                return HttpResponse('Invalid header found: {}'.format(e.args[0]))
            
            messages.success(request, '<div class="my-5 alert alert-success alert-dismissible fade show"><strong>Success!</strong> We will try to contact you within 24 hours.<button type="button" class="close" data-dismiss="alert">&times;</button></div>',extra_tags='ilovepancakesupport')
            
            #return redirect('success')
            
    return render(request, 'pages/support.html', {'form': form})

def PricingView(request):
    return render(request, 'pages/pricing.html')

def BuyNowView(request):
    return render(request,'pages/buy-now.html')
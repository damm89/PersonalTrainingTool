from django.contrib import admin
from .models import *
    
class clientaccountsAdmin(admin.ModelAdmin):
    pass
    #form = clientaccounts
    
admin.site.register(ClientAccount, clientaccountsAdmin)



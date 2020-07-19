from django import forms
from django.forms.formsets import formset_factory

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Field, HTML, Fieldset, Div, ButtonHolder, Submit, Row, Column

from clientaccounts.models import ClientAccount

from .models import *
from .custom_layout_object import *

from .static_variables import *

class MealPlanForm(forms.Form):
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user')
        client_accounts = [(cl_acc.id,cl_acc.name) for cl_acc in ClientAccount.objects.filter(owner = user)]
        meal_plan_templates = [(mpt.id,mpt.name) for mpt in MealPlanTemplate.objects.filter(owner = user, is_working=True)]
        super(MealPlanForm, self).__init__(*args, **kwargs)

        self.fields['name'] = forms.CharField(
                widget = forms.TextInput(attrs={'placeholder':'required'}),
                required = True
            )
        
        self.fields['client_account'] = forms.ChoiceField(
                choices = client_accounts,
                required = True
            )
        
        self.fields['duration'] = forms.ChoiceField(
                widget = forms.Select(attrs={'class':'form-control'}),
                choices = DURATION_CHOICES,
                label = 'Meal Plan Duration',
                required = True
            )
        
        self.fields['mpt'] = forms.ChoiceField(
                choices = meal_plan_templates,
                required = True,
                label = 'Meal Plan Template'
            )
        
        self.fields['mpt_name'] = forms.CharField(
                widget=forms.HiddenInput(),
                required=True,
            )     

        self.fields['adjust_maintenance'] = forms.BooleanField(
            required = False
            )
        
        #self.fields['weight_type'] = forms.ChoiceField(
        #    widget = forms.Select(attrs={'class':'form-control'}),
        #    choices = ["oz", "gram"],
        #    label = "Meal weight type",
        #    required = True
        #)
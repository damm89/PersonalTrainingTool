from django import forms
from django.forms.formsets import formset_factory

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Field, HTML, Fieldset, Div, ButtonHolder, Submit, Row, Column

from .models import *
from .custom_layout_object import *

from .static_variables import *

class ClientForm(forms.Form):
    name = forms.CharField(
        widget=forms.TextInput(attrs={'placeholder': 'Name'}),
        required=True
    )

    gender = forms.ChoiceField(
        choices = GENDER_CHOICES,
        widget=forms.Select,
        required=True,
        initial = "Female"
    )

    age = forms.IntegerField(
        widget = forms.NumberInput(attrs={"min":"0", "max":"130"}),
        required=True,
    )
    
    email = forms.EmailField(
        required = True,
    )

    height = forms.CharField(
        widget=forms.NumberInput(attrs={"min":"0", "max":"250"}),
        required = True,
        label = False,
    )

    height_type = forms.ChoiceField(
        choices = [('cm',)*2,('ft',)*2],
        widget=forms.Select(attrs={'class':'input-group-text'}),
        initial = 'cm',
        label = False,
    )

    height_add = forms.CharField(
        widget=forms.NumberInput(attrs={"min":"0", "max":"11","style":"display:none;"}),
        required = False,
        label = False,
    )

    weight = forms.CharField(
        widget=forms.NumberInput(attrs={"min":"0", "max":"800", "step":"0.1"}),
        required = True,
        label = False,
    )

    weight_type = forms.ChoiceField(
        choices = [('kg',)*2,('lbs',)*2,('st',)*2],
        widget=forms.Select(attrs={'class':'input-group-text'}),
        initial = 'kg',
        label = False,
    )

    weight_add = forms.CharField(
        widget=forms.NumberInput(attrs={"min":"0", "max":"13.9","step":"0.1","style":"display:none;"}),
        required = False,
        label = False,
    )

    activity_level = forms.ChoiceField(
        choices = ACTIVITY_LEVEL_CHOICES,
        widget = forms.Select,
        required=True,
        initial = "1.2"
    )

    comments = forms.CharField(
        widget = forms.Textarea(attrs={'placeholder':"Anything you'd like to add?"}),
        required=False
    )
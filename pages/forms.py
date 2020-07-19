from django import forms

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Field, HTML

class SupportForm(forms.Form):
    name = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Your name'}),required=True)
    email = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Your email address'}),required=True)
    message = forms.CharField(widget=forms.Textarea(attrs={'placeholder': 'Describe your problem'}),required=True,label='')
    
    helper = FormHelper()
    #helper.form_class = 'form-horizontal'
    helper.layout = Layout(
        Field('name', css_class='input-xlarge'),
        Field('email',css_class='input-xlarge'),
        Field('message',rows=3,css_class='input-xlarge'),
        HTML('<div class="ml-auto"><input type="submit" name="Submit" value="Submit" class="btn btn-primary btn-primary w-100" id="submit-id-submit"></div>')
    )
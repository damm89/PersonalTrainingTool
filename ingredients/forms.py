
from django import forms

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Field, HTML, Fieldset, Div, ButtonHolder, Submit, Row, Column

from ws.static_variables import WEIGHT_MULTIPLIERS


class IngredientTagForm(forms.Form):
    tag = forms.CharField(
        widget = forms.TextInput(attrs={'placeholder':"Add tag", 'style':"height:auto!important;"}),
        required=False
        )


class IngredientForm(forms.Form):
    name = forms.CharField(
        widget=forms.TextInput(attrs={'placeholder':"Required", 'required':'true'}),
        required=True,
        label='Name',
        )

    amount = forms.CharField(
        widget=forms.NumberInput(attrs={'placeholder':"Required", 'min':'0','style':'min-width:6em;','step':'0.1', 'required':'true'}),
        required=True,
        label='',
        )

    amount_type = forms.CharField(
        widget=forms.Select(
            choices=[(_,_) for _ in WEIGHT_MULTIPLIERS],
            attrs={'style':'min-width:6em;', 'required':'true'}
            ),
        required=True,
        label='',
        )

    original_protein = forms.FloatField(
        widget=forms.NumberInput(attrs={'placeholder':"Required", 'min':'0','step':'0.1', 'required':'true'}),
        required=True,
        label='',
        )

    original_carbs = forms.FloatField(
        widget=forms.NumberInput(attrs={'placeholder':"Required", 'min':'0','step':'0.1', 'required':'true'}),
        required=True,
        label="",
        )

    original_sugars = forms.FloatField(
        widget=forms.NumberInput(attrs={'min':'0','step':'0.1'}),
        required=False,
        label="",
        )

    original_fibers = forms.FloatField(
        widget=forms.NumberInput(attrs={'min':'0','step':'0.1'}),
        required=False,
        label="",
        )

    original_fats = forms.FloatField(
        widget=forms.NumberInput(attrs={'placeholder':"Required", 'min':'0','step':'0.1', 'required':'true'}),
        required=True,
        label="",
        )

    original_saturated_fats = forms.FloatField(
        widget=forms.NumberInput(attrs={'min':'0','step':'0.1'}),
        required=False,
        label="",
        )

    original_unsaturated_fats = forms.FloatField(
        widget=forms.NumberInput(attrs={'min':'0','step':'0.1'}),
        required=False,
        label="",
        )

    original_salt = forms.FloatField(
        widget=forms.NumberInput(attrs={'min':'0','step':'0.1'}),
        required=False,
        label="",
        )

    comments = forms.CharField(
        widget = forms.Textarea(attrs={'placeholder':"Anything you'd like to add?"}),
        required=False,
        label="Comments",
        )

    helper = FormHelper()
    helper.layout = Layout(
        HTML('<div class="ml-auto"><input type="submit" name="Submit" value="Submit" class="btn btn-primary btn-primary w-100" id="submit-id-submit"></div>')
        )

    def clean(self):
        cleaned_data = super().clean()
        for key in cleaned_data:
            if key.find('original') != -1 and cleaned_data[key] is None:
                cleaned_data[key] = float(0)

        f = float(cleaned_data.get('original_fats'))
        sf = float(cleaned_data.get('original_saturated_fats'))
        uf = float(cleaned_data.get('original_unsaturated_fats'))

        fat_error = False
        if sf + uf > f:
            self.add_error("original_fats", "Fats needs to be greater than or equal to saturated and unsaturated combined.")
            fat_error = True
        
        c = float(cleaned_data.get('original_carbs'))
        s = float(cleaned_data.get('original_sugars'))

        sugar_error = False
        if s > c:
            self.add_error("original_carbs", "Carbs need to be greater than or equal to sugars.")
            sugar_error = True
        
        if fat_error or sugar_error:
            raise forms.ValidationError("", code='invalid')

        return cleaned_data


class UploadIngredientForm(forms.Form):
    filename = forms.FileField(required=True)
    name = forms.ChoiceField(required=True)
    amount = forms.ChoiceField(required=True)
    amount_type = forms.ChoiceField(required=False)
    protein = forms.ChoiceField(required=True)
    carbs = forms.ChoiceField(required=True)
    sugars = forms.ChoiceField(required=False)
    fibers = forms.ChoiceField(required=False)
    fats = forms.ChoiceField(required=True)
    saturated_fats = forms.ChoiceField(required=False)
    unsaturated_fats = forms.ChoiceField(required=False)
    salt = forms.ChoiceField(required=False)
    comments = forms.ChoiceField(required=False)
    tag = forms.ChoiceField(required=False)
    helper = FormHelper()
    helper.form_class = 'form-horizontal'
    helper.label_class = 'col-lg-3'
    helper.field_class = 'col-lg-6'
    helper.layout = Layout(
        'filename',
        'name',
        'amount',
        'amount_type',
        'protein',
        'carbs',
        'sugars',
        'fibers',
        'fats',
        'saturated_fats',
        'unsaturated_fats',
        'salt',
        'comments',
        'tag',
    )

from django import forms

from ws.static_variables import WEIGHT_MULTIPLIERS

class CustomBaseFormSet(forms.formsets.BaseFormSet):
    def __init__(self, *args, **kwargs):
        super(CustomBaseFormSet, self).__init__(*args, **kwargs)

    def _construct_form(self, *args, **kwargs):
        return super(CustomBaseFormSet, self)._construct_form(*args, **kwargs)



class MealForm(forms.Form):
    name = forms.CharField(
        widget=forms.TextInput(attrs={'placeholder': 'Name', 'required':'true'}),
        label = 'Name',
        required = True,
        )
    category = forms.CharField(
        widget = forms.TextInput(attrs={'placeholder':"Breakfast, fruit, etc"}),
        required = False,
        )
    
    comment = forms.CharField(
        widget = forms.Textarea(attrs={'placeholder':"Please add comments/instructions for meal", "rows":5}),
        required = False,
        label = "Comments/instructions",
    )

    add_ing_comment = forms.BooleanField(
        required = False,
    )


class MealIngredientForm(forms.Form):
    """
    Creates meal ingredient form.
    """
    original_quantity = forms.FloatField(
        widget = forms.NumberInput(attrs={'min': '0','class':'px-1 px-md-2','style':'min-width:2em;','step':'0.1', 'disabled':'true', 'required':'true'}),
        label = '',
        )
    
    ingredient_name = forms.CharField(
        widget=forms.TextInput(),
        label='Name',
        required=True,
        )

    amount_type = forms.CharField(
        widget=forms.Select(
            choices=[(_,_) for _ in WEIGHT_MULTIPLIERS],
            attrs={'style':'min-width:3em;', 'class':'quantity-input px-0 px-md-2', 'disabled':'true', 'required':'true'}
            ),
        required=True,
        label='',
        )
        
    ingredient = forms.CharField(
        widget = forms.HiddenInput()
        )


class TagMealForm(forms.Form):
    """
    Creates tag meal form.
    Name not used for now
    """
    name = forms.CharField(
        widget=forms.TextInput(attrs={'placeholder': 'Prefix'}),
        label='Name',
        required=False,
        )

    category = forms.CharField(
        widget = forms.TextInput(attrs={'placeholder':"Breakfast, fruit, etc"}),
        required=False
        )

    comment = forms.CharField(
        widget = forms.Textarea(attrs={'placeholder':"Please add comments/instructions for meal", "rows":5}),
        required = False,
        label = "Comments/instructions",
    )

    add_ing_comment = forms.BooleanField(
        required = False,
    )


class TagMealIngredientForm(forms.Form):
    """
    Creates tag meal ingredient form (quantity - tag), which are hidden fields and get values inserted by js after clicking on submit link.
    """

    original_quantity = forms.FloatField(
        widget = forms.NumberInput(attrs={'min': '0','style':'min-width:5em;','step':'0.1', 'required':'true'}),
        label = '',
        required=True
        )
    
    amount_type = forms.CharField(
        widget=forms.Select(
            choices=[(_,_) for _ in WEIGHT_MULTIPLIERS],
            attrs={'style':'min-width:6em;', 'class':'quantity-input', 'required':'true'}
            ),
        required=True,
        label='',
        )
        
    tag = forms.CharField(
        widget=forms.HiddenInput(),
        required=True,
        )
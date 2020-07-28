import json

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.forms.models import model_to_dict
from django.http import HttpResponse
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_protect
from django.urls import reverse

from .models import *
from .forms import *

from ws.static_variables import SUCCESS_MESSAGE, ERROR_MESSAGE
from ws.forms import FormCleanedData

@login_required
def CreateIngredient(request):
    """
    Creates ingredient.
    """
    tags = [_.name for _ in IngredientTag.objects.only('owner','name').filter( owner = request.user )]

    if request.method == 'GET':
        form = IngredientForm()
        tag_form = IngredientTagForm()
        return render(request, 'ingredients/create.html', {'form':form, 'tag_form':tag_form, 'purpose':'add', 'tag_data_list':tags})

    else:
        form = IngredientForm(request.POST)
        tag_form = IngredientTagForm(request.POST)

        if form.is_valid():
            if tag_form.is_valid():
                ing_objects = []
                ingredient = Ingredient(**form.cleaned_data)
                ingredient.owner = request.user
                ingredient.save(tag_form=tag_form)
                ing_objects.append(ingredient)
                messages.success(request, SUCCESS_MESSAGE.format("You created ingredient: {}.".format(ingredient.name)),extra_tags='ilovepancakesclientaccounts')
                return HttpResponseRedirect(reverse('ingredients:ingredients')) 
                try:
                    pass

                except Exception:
                    for ing in ing_objects:
                        ing.delete()

        else:
            messages.error(request, ERROR_MESSAGE.format("Please check highlighted fields."),extra_tags='ilovepancakesclientaccounts')
            return render(request, 'ingredients/create.html', {'form':form, 'tag_form':tag_form, 'purpose':'add', 'tag_data_list':tags})


@login_required
def EditIngredient(request, ingredient_id):
    """
    Edits an ingredient.
    """
    ingredient = Ingredient.objects.get(pk=ingredient_id)
    initial_ingredient = model_to_dict(ingredient)
    form = IngredientForm(initial_ingredient)

    tag_dict = {}
    tag_dict['tag'] = ','.join([_['name'] for _ in ingredient.tag.values()])
    tag_form = IngredientTagForm(tag_dict)
    tags = [_.name for _ in IngredientTag.objects.only('owner','name').filter( owner = request.user )]

    if request.user == ingredient.owner:
        if request.method == "POST":
            form = IngredientForm(request.POST)
            tag_form = IngredientTagForm(request.POST)

            if form.is_valid():
                if tag_form.is_valid():

                    try:
                        for k in form.cleaned_data:
                            setattr(ingredient, k, form.cleaned_data[k])

                        ingredient.save(tag_form=tag_form)
                        messages.success(request, SUCCESS_MESSAGE.format("You successfully edited ingredient: {}.".format(form.cleaned_data['name'])),extra_tags='ilovepancakesclientaccounts')
                        return HttpResponseRedirect(reverse('ingredients:ingredients')) 

                    except Exception:
                        messages.error(request, ERROR_MESSAGE.format("Please check highlighted fields."),extra_tags='ilovepancakesclientaccounts')
                        return render(request, 'ingredients/create.html', {'form':form, 'tag_form':tag_form, 'purpose':'add', 'tag_data_list':tags})

        return render(request, 'ingredients/create.html', {'form': form, 'ingredient':ingredient, 'tag_form':tag_form, 'purpose':'edit', 'tag_data_list':tags})
    
    else:
        messages.error(request, ERROR_MESSAGE.format('You are not the owner of this ingredient.'),extra_tags='ilovepancakesclientaccounts')
        return render(request, 'ingredients/create.html', {'form':form, 'tag_form':tag_form, 'purpose':'add', 'tag_data_list':tags})


@login_required
def UploadIngredient(request):
    if request.method == "GET":
        form = UploadIngredientForm()
        return render(request, 'ingredients/upload-ingredients.html', {'form': form})

    else:
        messages.error(request, ERROR_MESSAGE.format('No'),extra_tags='ilovepancakesclientaccounts')
        return HttpResponseRedirect(reverse('ingredient:upload-ingredients')) 


@login_required
@csrf_protect
def MassUploadIngredients(request):
    message = ''
    if request.method == "POST":
        if request.is_ajax():
            ingredients_dict = json.loads(request.POST.get('ingredientsData', None))
            ingredients = []

            try:
                for ingredient in ingredients_dict:
                    if 'tag' in ingredients_dict[ingredient]['cleaned_data']:
                        tag_form = ingredients_dict[ingredient]['cleaned_data'].pop('tag')
                    else:
                        tag_form = ''

                    ingredient = Ingredient(**ingredients_dict[ingredient]['cleaned_data'])
                    ingredient.owner = request.user
                    ingredient.save(tag_form=tag_form)
                    ingredients.append(ingredient)

                response = HttpResponse(json.dumps({'message': 'Successfully uploaded {} ingredient(s).'.format(len(ingredients))}),
                    content_type='application/json')
                response.status_code = 200
                return response

            except Exception:
                for ing in ingredients:
                    ing.delete()
            
                message = "Something unforeseeable happened."

        else:
            message = "Not an ajax request."

    else:
        message = 'This is not a POST request.'

    messages.error(request, ERROR_MESSAGE.format(message),extra_tags='ilovepancakesclientaccounts')
    response = HttpResponse(json.dumps({'message': message}), 
                content_type='application/json')
    response.status_code = 400
    return response

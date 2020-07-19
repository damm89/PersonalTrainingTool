from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.forms.formsets import formset_factory
from django.forms.models import model_to_dict
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

from .models import *
from .forms import *
from .functions import *

from ingredients.models import Ingredient, IngredientTag

from ws.static_variables import ERROR_MESSAGE, SUCCESS_MESSAGE

@login_required
def CreateMeal(request):
    """
    Allows a user to create meals.
    """

    user = request.user
    categories = [_.name for _ in MealCategory.objects.only('name','owner').filter(owner = user)]
    MealIngredientFormSet = formset_factory(MealIngredientForm, formset=CustomBaseFormSet)

    if request.method == "GET":
        meal_form = MealForm()
        meal_ingredient_formset = MealIngredientFormSet()
        return render(request,'meals/create.html', {'meal_form': meal_form, 'meal_ingredient_formset':meal_ingredient_formset, 'purpose':'add', 'category_data_list':categories}) 

    if request.method == "POST":
        meal_form = MealForm(request.POST)
        meal_ingredient_formset = MealIngredientFormSet(request.POST)

        if meal_form.is_valid():
            name = meal_form.cleaned_data.get('name').capitalize()
            category = meal_form.cleaned_data.get('category')
            comment = meal_form.cleaned_data.get('comment')
            add_ing_comment = meal_form.cleaned_data.get('add_ing_comment')

            if meal_ingredient_formset.is_valid():
                if len(meal_ingredient_formset) == 0:
                    messages.error(request, ERROR_MESSAGE.format("You need to add an ingredient before you submit your meal."),extra_tags='ilovepancakesclientaccounts')
                
                else:
                    meal_objects = []
                    m = meal_data(
                        request = request,
                        name = name,
                        category = category,
                        meal_ingredient_formset = meal_ingredient_formset,
                        comment = comment,
                        add_ing_comment = add_ing_comment,
                        )

                    meal_objects.append(m)

                    messages.success(request, SUCCESS_MESSAGE.format("You created meal: {}.".format(m.name)),extra_tags='ilovepancakesclientaccounts')
                    return HttpResponseRedirect(reverse('meals:meals')) 

        return render(request, 'meals/create.html', {'meal_form': meal_form,'meal_ingredient_formset':meal_ingredient_formset, 'purpose':'add', 'category_data_list':categories})


@login_required
def EditMeal(request, meal_id):
    """
    Allows a user to edit a meal.
    """
    user = request.user
    categories = [_.name for _ in MealCategory.objects.only('name','owner').filter( owner = user )]
    MealIngredientFormSet = formset_factory(MealIngredientForm, formset=CustomBaseFormSet, extra=0)
    meal = Meal.objects.get(pk = meal_id)
    meal_ingredients = MealIngredient.objects.filter(meal = meal)

    if meal.owner == request.user:
        if request.method == "GET":
            meal_dict = model_to_dict(meal)
            meal_dict['category'] = ','.join([_['name'] for _ in meal.category.values()])
            meal_form = MealForm(meal_dict)

            initial_data = [model_to_dict(_) for _ in meal_ingredients]
            for ingr in initial_data:
                ingr['name'] = Ingredient.objects.only('name').get(pk = ingr['ingredient']).name
            meal_ingredient_formset = MealIngredientFormSet(initial = initial_data)

            return render(request,'meals/create.html', {'meal_form': meal_form, 'meal_ingredient_formset':meal_ingredient_formset, 'meal':meal, 'purpose':'edit', 'category_data_list':categories}) 

        if request.method == "POST":
            meal_form = MealForm(request.POST)
            meal_ingredient_formset = MealIngredientFormSet(request.POST)

            if meal_form.is_valid():
                name = meal_form.cleaned_data.get('name').capitalize()
                category = meal_form.cleaned_data.get('category')
                comment = meal_form.cleaned_data.get('comment')
                add_ing_comment = meal_form.cleaned_data.get('add_ing_comment')

                if meal_ingredient_formset.is_valid():
                    if len(meal_ingredient_formset) == 0:
                        messages.error(request, ERROR_MESSAGE.format("You need to add an ingredient before you submit your meal."),extra_tags='ilovepancakesclientaccounts')
                    
                    else:
                        m = meal_data(
                            category = category,
                            meal = meal,
                            meal_ingredient_formset = meal_ingredient_formset,
                            name = name,
                            request = request,
                            comment = comment,
                            add_ing_comment = add_ing_comment,
                            )

                        messages.success(request, SUCCESS_MESSAGE.format("You edited meal: {}.".format(name)),extra_tags='ilovepancakesclientaccounts')
                        return HttpResponseRedirect(reverse('meals:meals')) 
                        
            return render(request, 'meals/create.html', {'meal_form': meal_form, 'meal_ingredient_formset':meal_ingredient_formset, 'meal':meal, 'purpose':'edit', 'category_data_list':categories})
    else:
        messages.error(request, ERROR_MESSAGE.format('You are not the owner of this meal.'),extra_tags='ilovepancakesclientaccounts')
        return HttpResponseRedirect(reverse('meals:meals')) 


@login_required
def CreateTagMeal(request):
    """
    Allows a user to create meals from tags.
    """
    
    TagMealIngredientFormSet = formset_factory(TagMealIngredientForm, formset=CustomBaseFormSet)
    user = request.user
    categories = [_.name for _ in MealCategory.objects.filter(owner = user)]
    ingredient_tags = [(_.id,_.name,_.used) for _ in IngredientTag.objects.filter(owner = user, used__gt = 0).order_by('name')]
    tags = [_[1] for _ in ingredient_tags]
    tags_used = {_[0]:_[-1] for _ in ingredient_tags}
    tags_ids = {_[1]:_[0] for _ in ingredient_tags}
    ingredient_tags = [(_[0], _[1]) for _ in ingredient_tags]

    if request.method == "GET":
        tag_meal_form = TagMealForm()
        tag_meal_ingredient_formset = TagMealIngredientFormSet()
        return render(request,'meals/tags/create.html', {'tag_meal_form':tag_meal_form, 'tag_meal_ingredient_formset':tag_meal_ingredient_formset, 'category_data_list':categories, 'tags_data_list':tags, 'tags_used':tags_used, 'tags_ids':tags_ids}) 

    if request.method == "POST":
        tag_meal_form = TagMealForm(request.POST)
        tag_meal_ingredient_formset = TagMealIngredientFormSet(request.POST)

        if tag_meal_form.is_valid():
            category = tag_meal_form.cleaned_data.get('category')
            comment = tag_meal_form.cleaned_data.get('comment')
            add_ing_comment = tag_meal_form.cleaned_data.get('add_ing_comment')

            if tag_meal_ingredient_formset.is_valid():
                if len(tag_meal_ingredient_formset) == 0:
                    messages.error(request, ERROR_MESSAGE.format("You need to add an ingredient before you submit your meal."),extra_tags='ilovepancakesclientaccounts')
                
                else:
                    m_objects = []
                    #try:
                    m_objects += tag_meal_data(
                        request = request,
                        category = category,
                        tag_meal_ingredient_formset = tag_meal_ingredient_formset,
                        comment = comment,
                        add_ing_comment = add_ing_comment,
                        )

                    messages.success(request, SUCCESS_MESSAGE.format("{}".format("You created {} new meals.".format(len(m_objects)))),extra_tags='ilovepancakesclientaccounts')
                    return HttpResponseRedirect(reverse('meals:meals')) 
                    
                    #except Exception:
                    #    for m in m_objects:
                    #        m.delete()
                    #    messages.error(request, ERROR_MESSAGE.format("Check your inputs."),extra_tags='ilovepancakesclientaccounts')
            else:
                messages.error(request, ERROR_MESSAGE.format("Tag Meal Ingredient Formset Invalid"),extra_tags='ilovepancakesclientaccounts')
        else:
            messages.error(request, ERROR_MESSAGE.format("Tag Meal Formset Invalid"),extra_tags='ilovepancakesclientaccounts')

        return render(request, 'meals/tags/create.html', {'tag_meal_form': tag_meal_form,'tag_meal_ingredient_formset':tag_meal_ingredient_formset, 'category_data_list':categories, 'tags_data_list':tags, 'tags_used':tags_used, 'tags_ids':tags_ids})


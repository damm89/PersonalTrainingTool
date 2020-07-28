import itertools
import json 

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Prefetch, F, Value, CharField, ExpressionWrapper
from django.db.models.functions import Concat
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render
from django.urls import reverse
from django.views.decorators.csrf import csrf_protect
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.postgres.search import SearchQuery, SearchRank

from ingredients.models import *
from mealplans.models import *
from meals.models import *
from clientaccounts.models import *

from .functions import get_model_object
from .static_variables import CATEGORY_DATA

from meals.functions import get_ingredients_with_tags
from mealplans.functions import meal_2_meal_dict, create_meal_plan

from ws.forms import FormCleanedData
from ws.static_variables import ERROR_MESSAGE, SUCCESS_MESSAGE

from django.urls import reverse

@login_required
def searchSuggestion(request, category):
    if request.method == 'GET':
        contains = request.GET.get('contains', False)
        query = SearchQuery(contains)
        try:
            object_cat = get_model_object(category)
            if object_cat != None:
                results = list(object_cat.objects.annotate(
                    rank=SearchRank(F('search_name'),
                    query)).order_by('-rank')[:5].values_list('name', flat=True))
                
                for _ in object_cat.objects.annotate(rank=SearchRank(F('search_name'),query)).order_by('-rank').values():
                    print(_['name'], _['rank'])

                if len(results) == 0:
                    return JsonResponse({'status_code':404}, safe=False)
                else:
                    return JsonResponse({'status_code':200, 'results':results}, safe=False)
                    
        except ObjectDoesNotExist:
            return JsonResponse({'status_code':404}, safe=False)


@login_required
def APIView(request, category):
    """
    Retrieves all items that belong to request.user from category = category.
    Called by the django templator of html lists such as: 
        clientaccounts/list.html,
        ingredients/list.html,
        ingredients/tags/list.html,
        meals/list.html,
        meals/categories/list.html,
        mealplans/list.html,
        mealplans/templates/list.html,
    As well as by an ajax call throughh the search function on those pages.
    By default returns lte 20 rows of data ordered alphabetically by name.

    To implement: order by other categories and other filters
    """


    if request.method == "GET":
        contains = request.GET.get('contains', False)
        intent = request.GET.get('intent', False)

        if intent != 'data-list':
            number_of_rows_done = request.GET.get('number_of_rows_done', None)
            number_of_rows = request.GET.get('number_of_rows', None)
        else:
            number_of_rows_done = 0
            number_of_rows = 5

        order_by = request.GET.get('order_by', False)

        if number_of_rows == None:
            number_of_rows = 20
        else:
            number_of_rows = int(number_of_rows)
        
        if number_of_rows_done == None:
            number_of_rows_done = 0
        else:
            number_of_rows_done = int(number_of_rows_done)
        
        if order_by == False:
            order_by = ['name']
        else:
            order_by = [order_by,'name']
        
        object_cat = get_model_object(category)
        
        context_keys = ['cols', 'only', 'buttons', 'hidden_cols']
        context = {}
        for ckey in context_keys:
            if ckey in CATEGORY_DATA[category]:
                context[ckey] = CATEGORY_DATA[category][ckey]

        if contains:
            contains = contains.strip(' ').lower()
            data = list(object_cat.objects.filter(owner = request.user, name__icontains=contains).select_related().order_by(*order_by)[number_of_rows_done:number_of_rows].values(*context['only']))
        else:
            data = list(object_cat.objects.filter(owner = request.user).select_related().order_by(*order_by)[number_of_rows_done:number_of_rows].values(*context['only']))

        if intent == 'update':
            if request.is_ajax():
                return JsonResponse(data, safe=False)
            else:
                return HttpResponse(json.dumps(data), content_type='application/json')

        else:
            context[category.replace('-','')] = data
            context['cat_str'] = category
            return render(request, '{}/list.html'.format(category.replace('-','/')), context)


@login_required
def GetItemData(request, category):
    """
    Retrieves specific data of specified objects 
    through an ajax call. 
    Returns a data JSON.
    Every category has their own description.
    """
    if request.method == "GET": 
        if request.is_ajax():
            data = {}
            if category == "ingredient_data":
                """
                Called by the ajax function on create_meal.html
                that is triggered by searching ingredients in the
                ingredient search input.
                Returns a JSON with nutritional data on those ingredients.
                """
                ingredient_ids = request.GET.get('ingredient_ids', None)
                data_keys = request.GET.get('data_keys', None)
                for ing_id,data_key in zip(ingredient_ids.split(','),data_keys.split(',')):
                    ing = Ingredient.objects.filter(owner = request.user).only(*['protein','carbs','fats','name']).get(pk = ing_id)
                    if ing:
                        data[data_key] = {
                            'kcals':int(ing.kcals),
                            'protein':round(float(ing.protein),1),
                            'carbs':round(float(ing.carbs),1),
                            'fats':round(float(ing.fats),1),
                            'name':ing.name,
                            }
                            
            elif category == "del_ingredient":
                ingredient_id = request.GET.get('ingredient_id',None)
                if ingredient_id != None:
                    ing = Ingredient.objects.get(owner = request.user, pk = ingredient_id)
                    meal_count = Meal.objects.filter(owner = request.user, mealingredient__ingredient = ing).distinct().count()
                    data['meal_count'] = meal_count
                    if meal_count != 1:
                        data['data'] = "This will delete {} meals. Continue?".format(meal_count)
                    else:
                        data['data'] = "This will delete 1 meal. Continue?"

            elif category == "mealcount":
                """
                Called by meals/tags/create.html when a tag is changed
                in the tag input.
                Returns a combinatory meal count for that specific 
                combinations of ingredient tags.
                """
                tags_names = request.GET.get('tags_names', None)
                if tags_names != None:
                    ingredients = []
                    total_ingredients = []
                    tags_names = json.loads(tags_names)
                    for tags in tags_names:
                        cleaned_tags = [_.strip(' ').lower() for _ in tags_names[tags].split(';:') if _.replace(' ','') != '']
                        ingredients, total_ingredients = get_ingredients_with_tags(request, cleaned_tags, ingredients, total_ingredients)

                    meal_count = str(len(list(itertools.product(*ingredients))))
                    data['meal_count'] = meal_count

            elif category == 'templatecount':
                """
                Used in meals_categories.html to determine
                how many templates will be impacted by the 
                deletion of this specific category.
                Returns template count.
                """
                category_id = request.GET.get('category_id', None)
                if category_id != None:
                    meal_cats = [MealCategory.objects.get(owner = request.user, pk = category_id)]
                    mpt_count = int(MealPlanTemplate.objects.filter(owner = request.user, daymealplantemplate__mealmealplantemplate__meal_categories__in=meal_cats).distinct().count())
                    if mpt_count != 1:
                        data['data'] = "This will impact {} mealplan templates. Continue?".format(mpt_count)
                    else:
                        data['data'] = "This will impact 1 mealplan template. Continue?"
            

            elif category == 'alternative_meal':
                """
                Called by show_meal_plan.html to get 
                an alternative meal by meal id for that specific 
                meal time.
                Returns an alternative meal.
                """
                meal_pk = request.GET.get('meal_pk', None)
                if meal_pk != None:
                    try:
                        meal = Meal.objects.filter(owner = request.user).prefetch_related(
                                    Prefetch(
                                        'mealingredient_set',
                                        queryset = MealIngredient.objects.filter(owner = request.user).only('amount_type','quantity','ingredient').select_related('ingredient').order_by('ingredient__name').all(),
                                        to_attr='mealingredients'
                                    )
                                ).get(pk = meal_pk)

                        alternatives = request.GET.get('alternatives', None)
                        if alternatives != None:
                            alternatives = json.loads(alternatives)
                        else:
                            alternatives = []

                        meal_kcal = request.GET.get('meal_kcal', None)
                        if meal_kcal != None:
                            meal_kcal = float(meal_kcal)
                        else:
                            meal_kcal = 0

                        data['status_code'] = 200
                        data['meal_dict'] = meal_2_meal_dict(meal, alternatives, meal_kcals_new=meal_kcal)

                    except Meal.DoesNotExist:

                        meal_plan_pk = request.GET.get('meal_plan_pk', None)
                        if meal_plan_pk == None:
                            data['status_code'] = 404
                            data['message'] = "Could not retrieve meal plan id."
                            return JsonResponse(data)

                        else:
                            meal_plan = MealPlan.objects.get(pk = meal_plan_pk)
                            meal_plan_form = json.loads(meal_plan.form)
                            meal_plan_form = FormCleanedData(meal_plan_form)

                            meal_plan = create_meal_plan(request, meal_plan_form, meal_plan_obj=meal_plan)
                            data['status_code'] = 201
                            data['meal_plan'] = json.dumps(meal_plan)
                            return JsonResponse(data)

            if len(data.keys()) > 0:
                return JsonResponse(data)

            else:
                message = "No data found." 

        else:
           message = "This is not an AJAX request." 

    else:
        message = "This is not a GET request."

    data['message'] = message
    data['status_code'] = 400
    return JsonResponse(data)


@csrf_protect
@login_required
def DeleteItem(request, category, item_id):
    """
    Deletes item from database - no retrieval possible.
    """
    if request.is_ajax():
        if request.method == "POST":

            if not category:
                category = request.POST.get('category', False)

            if category == 'clientaccounts':
                obj = ClientAccount.objects.filter(owner = request.user).get(pk=item_id)
                obj_name = 'client account'

            elif category == "meals":
                obj = Meal.objects.filter(owner = request.user).get(pk=item_id)
                obj_name = 'meal'

            elif category == "ingredients":
                obj = Ingredient.objects.filter(owner = request.user).get(pk=item_id)
                obj_name = 'ingredient'

                old_tags = list(obj.tag.all())
                for tag in old_tags:
                    tag.used -= 1
                    tag.save()

                Meal.objects.filter(owner = request.user, mealingredient__ingredient=obj).delete()

            elif category == 'ingredients-tags':
                """
                Deletes ingredient tags and also deletes it from
                the related ingredient's tags list.
                """
                obj = IngredientTag.objects.filter(owner = request.user).get(pk=item_id)
                obj_name = 'ingredient tag'
                ingredients = Ingredient.objects.only('tag','tags').filter(tag = obj, owner = request.user)
                
                for ingredient in ingredients:
                    ingredient.remove_tag(obj)

            elif category == 'meals-categories':
                """
                Deletes meal category and edits the related the meal plan 
                template.
                If there are no meal categories left for that specific meal
                the meal plan template is afunctional and is tagged as 
                is_working = False, 
                status = "Not working".
                Otherwise, the meal plan template is tagged as:
                status = "Not working as intended"
                """
                obj = MealCategory.objects.filter(owner = request.user).get(pk=item_id)
                obj_name = 'meal category'
                meals = Meal.objects.only('category','categories').filter(category = obj, owner = request.user)
                for meal in meals:
                    meal.category.remove(obj)
                    categories = meal.categories.lower().split(', ')
                    categories.remove(obj.name.lower())
                    meal.categories = ', '.join(categories)
                    meal.save()
                
                mpts = list(MealPlanTemplate.objects.only('template').filter(owner = request.user, daymealplantemplate__mealmealplantemplate__meal_categories__in=[obj]).prefetch_related(
                            Prefetch(
                                'daymealplantemplate_set',
                                queryset = DayMealPlanTemplate.objects.filter(owner = request.user).only('day_no').filter(mealmealplantemplate__meal_categories__in=[obj]).prefetch_related(
                                            Prefetch(
                                                'mealmealplantemplate_set', 
                                                queryset = MealMealPlanTemplate.objects.filter(owner = request.user).only('meal_no','meal_categories').filter(meal_categories__in = [obj]).prefetch_related(
                                                    Prefetch(
                                                        'meal_categories',
                                                        queryset = MealCategory.objects.filter(owner = request.user).all(),
                                                        to_attr = 'mcats'
                                                    )
                                                ), 
                                                to_attr = 'mmpt'
                                                )
                                            ).distinct(),
                                to_attr = 'dmpt'
                            )
                        ).distinct()
                    )

                for mpt in mpts:
                    data = json.loads(mpt.template)
                    is_working = True
                    for dmpt in mpt.dmpt:
                        day = 'd' + str(dmpt.day_no)
                        for mmpt in dmpt.mmpt:
                            mmpt.mcats.remove(obj)
                            mmpt.save()
                            meal =  day + 'm' + str(mmpt.meal_no)
                            data[day][meal]['mealCats'] = ";:".join([str(_.id) for _ in mmpt.mcats])
                            if len(mmpt.mcats) == 0:
                                is_working = False

                    mpt.template = data
                    if is_working:
                        mpt.status = "Not working as intended"
                    else:
                        mpt.status = "Not working"
                        mpt.is_working = is_working
                    mpt.save()
            
            elif category == 'mealplans-templates':
                obj = MealPlanTemplate.objects.filter(owner = request.user).get(pk=item_id)
                obj_name = 'meal plan template'

            elif category == 'mealplans':
                obj = MealPlan.objects.filter(owner = request.user).get(pk=item_id)
                obj_name = 'mealplan'

            name = obj.name
            if request.user == obj.owner:
                obj.delete()
                status_code = "200"
                message = "Successfully deleted {}: {}.".format(obj_name, name)

            else:
                status_code = "403"
                message = "You are not the owner of {}: {}.".format(obj_name, name)
        else:
            status_code = "403"
            message = "This is not a POST request"

    else:
        status_code = "403"
        message = "This is not an AJAX request"

    data = {'message':message,
            'status_code':status_code}
    return JsonResponse(data)

import json

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from django.urls import reverse
from django.views.decorators.csrf import csrf_protect


from .models import *
from .functions import *
from .forms import *

from meals.models import MealCategory

from ws.static_variables import ERROR_MESSAGE, SUCCESS_MESSAGE


@csrf_protect
@login_required
def CreateMealPlanTemplate(request):
    """
    Creates a meal plan template.
    POST needs to be called through ajax.
    """
    if request.method == 'GET':
        meal_cat2id = {_.name.lower():_.id for _ in MealCategory.objects.only('owner','name','id').filter(owner = request.user)}
        meal_cat = [_.lower() for _ in meal_cat2id]

        context = {
            'purpose':'add',
            'cat_data_list': meal_cat,
            'cat_id_list':meal_cat2id,
            }
        return render(request, 'mealplans/templates/create.html', context)

    elif request.method == 'POST':
        data = {}
        if request.is_ajax():
            data = json.loads(request.POST.get('dataDict'))
            name = request.POST.get('name')
            mpt = MealPlanTemplate(owner = request.user, name = name, template=json.dumps(data, sort_keys=True), is_working=True, status="Working")
            mpt.save(data=data)

        else:
            data['message'] = 'Error'
    
        return JsonResponse(data, safe=False)

@csrf_protect
@login_required
def EditMealPlanTemplate(request, item_id):
    """
    Retrieves the old meal template and updates it.
    Deletes all days and uploads complete new template instead of updating.
    POST needs to be called through ajax.
    """
    if request.method == 'GET':
        mpt = MealPlanTemplate.objects.get(owner = request.user, pk = item_id)
        meal_cat2id = {_.name.lower():_.id for _ in MealCategory.objects.only('name','owner').filter(owner = request.user)}
        meal_cat = [_.lower() for _ in meal_cat2id]
        context = {
            'mpt_name': mpt.name,
            'mpt_id': mpt.id,
            'data': mpt.template,
            'purpose': 'edit',
            'cat_data_list': meal_cat,
            'cat_id_list': meal_cat2id,
            }
        return render(request, 'mealplans/templates/create.html', context)

    elif request.method == 'POST':
        data = {}
        if request.is_ajax():
            data = json.loads(request.POST.get('dataDict'))
            name = request.POST.get('name')

            mpt = MealPlanTemplate.objects.get(owner = request.user, pk = item_id)
            mpt.name = name
            mpt.template = json.dumps(data, sort_keys=True)
            mpt.is_working = True
            mpt.status = "Working"

            # Delete old days and meals
            DayMealPlanTemplate.objects.filter(mealplantemplate = mpt, owner = request.user).delete()
            mpt.save(data=data)

        else:
            data['message'] = 'Error'
    
        return JsonResponse(data, safe=False)


@login_required
def CreateMealPlan(request):
    user = request.user
    if request.method == "GET":
        meal_plan_form = MealPlanForm(user = user)
        return render(request, 'mealplans/create.html', {'meal_plan_form': meal_plan_form})
    
    elif request.method == 'POST':
        meal_plan_form = MealPlanForm(request.POST, user = user)

        if meal_plan_form.is_valid():
            
            try:
                mealplan = create_meal_plan(request, meal_plan_form)
                messages.success(request, SUCCESS_MESSAGE.format("You created {}.".format(mealplan.name)),extra_tags='ilovepancakesclientaccounts')
                return HttpResponseRedirect(reverse('mealplans:mealplans')) 
            
            except Exception as e:
                messages.error(request, ERROR_MESSAGE.format(e),extra_tags='ilovepancakesclientaccounts')
                return render(request, 'mealplans/create.html', {'meal_plan_form': meal_plan_form})
        
        else:
            messages.error(request, ERROR_MESSAGE.format("Form invalid"),extra_tags='ilovepancakesclientaccounts')

        return render(request, 'mealplans/create.html', {'meal_plan_form': meal_plan_form})


@login_required
def ShowMealPlan(request, item_id):
    meal_plan = MealPlan.objects.filter(owner = request.user).select_related('client_account').get(pk = item_id)
    if request.user == meal_plan.owner:
        if request.method == 'GET':
            return render(request, 'mealplans/show.html', {
                'meal_plan_id': item_id,
                'meal_plan': meal_plan.meal_plan,
                'start_weight': meal_plan.start_weight,
                'proj_weight': meal_plan.end_weight,
                'client_account': meal_plan.client_account,
                'proj_maintenance': meal_plan.end_maintenance})
    

@login_required
@csrf_protect
def EditMealPlan(request, item_id):
    message = ''
    if request.method == "POST":
        if request.is_ajax():
            meal_plan_dict = json.loads(request.POST.get('mealPlanData', None))

            meal_plan = MealPlan.objects.filter(owner = request.user).get(pk=item_id)
            meal_plan.meal_plan = json.dumps(meal_plan_dict)
            meal_plan.save()
            data = {'status_code':200, 'message':"You saved {}.".format(meal_plan.name)}
            return JsonResponse(data)
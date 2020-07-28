import json
import random
from django.db.models import Prefetch

from .my_exceptions import *
from .static_variables import HOUR_VALUES
from .models import *

from clientaccounts.models import ClientAccount
from meals.models import Meal, MealIngredient

from ws.functions import calculate_kcal, calculate_bmr


def create_ingredient_list_meal_plan(mealingredients, multiplier):
    ingredients_dict = {}
    for ingredient in mealingredients:
        unit = str(ingredient.amount_type)
        new_qty = multiplier * float(ingredient.quantity)
        name = str(ingredient.ingredient.name)

        if unit != 'piece':
            unit = 'gram'
            new_qty = new_qty * 100
        else:
            new_qty = new_qty
        
        if name in ingredients_dict:
            ingredients_dict[name]['u'].append(unit)
            ingredients_dict[name]['q'].append(new_qty)
        else:
            ingredients_dict[name] = {}
            ingredients_dict[name]['u'] = [unit]
            ingredients_dict[name]['q'] = [new_qty]
    
    return ingredients_dict


def meal_2_meal_dict(meal, alternatives, kcal_fraction=False, maintenance=False, meal_kcals_new=False):
    meal_kcals = float(meal.kcals)
    if kcal_fraction:
        meal_kcals_new = kcal_fraction * maintenance
    
    multiplier = meal_kcals_new / meal_kcals

    meal_dict = {}
    meal_dict['na'] = meal.name
    meal_dict['ca'] = float(meal.carbs) * multiplier
    meal_dict['fa'] = float(meal.fats) * multiplier
    meal_dict['fi'] = float(meal.fibers) * multiplier
    meal_dict['pr'] = float(meal.protein) * multiplier
    meal_dict['sal'] = float(meal.salt) * multiplier
    meal_dict['sf'] = float(meal.saturated_fats) * multiplier
    meal_dict['su'] = float(meal.sugars) * multiplier
    meal_dict['uf'] = float(meal.unsaturated_fats) * multiplier
    meal_dict['kc'] = meal_kcals_new 
    meal_dict['i'] = create_ingredient_list_meal_plan(meal.mealingredients, multiplier)
    meal_dict['co'] = meal.comment
    meal_dict['a'] = alternatives
    return meal_dict

class MealplanObject:
    """
    A meal plan object that creates and builds a mealplan
    """
    def __init__(self, request):
        self.meals = {}
        self.meal_plan = {}
        self.request = request
        self.ingredients = {}


    def get_category_meals(self):
        """
        Get meals belonging to the categories. Adds filters on querysets in a for loop.
        Creates meals dictionary if meals dictionary doesn't exist yet.
        """
        if self.categories in self.meals:
            pass
        else:
            categories = self.categories
            category = categories[0]
            meals = Meal.objects.filter(owner = self.request.user, category__name__icontains = category)
            if len(categories) > 1:
                for category in categories[1:]:
                    meals = meals.filter(category__name__icontains = category)

            meals = meals.order_by('name').prefetch_related(
                Prefetch(
                    'mealingredient_set',
                    queryset = MealIngredient.objects.filter(owner = self.request.user).only('amount_type','quantity','ingredient').select_related('ingredient').order_by('ingredient__name').all(),
                    to_attr='mealingredients'
                )
            )

            self.meals[categories] = {}
            self.meals[categories]['meals'] = list(meals.all())
            self.meals[categories]['kcal_fraction'] = float(self.kcal_fraction)
            self.meals[categories]['count'] = len(self.meals[categories]['meals'])
    

    def get_random_meal(self):
        """
        Selects a random meal from meals dictionary.
        """
        categories = self.categories
        count = self.meals[categories]['count']
        if count > 0:
            randint = random.randint(0,count-1)
            self.meal = self.meals[categories]['meals'][randint]
            self.alternatives = [(_.id,_.name) for i,_ in enumerate(self.meals[categories]['meals']) if i != randint]
            self.alternatives = [(self.meal.id, self.meal.name)] + self.alternatives
        else:
            raise NoMealsException({"message":"No meals found for category (combination): {}. Please check your meal plan template and your meals before trying again.".format(', '.join([_ for _ in self.categories]))})


    def add_meal_to_meal_plan(self):
        """
        Creates a meal dictionary that holds nutritional and meta data on the meal.
        Appends weekly grocery data to the grocery dictionary and meal dictionary to 
        meal plan dictionary.
        """
        self.meal_plan[self.week][self.day_of_week][self.time] = meal_2_meal_dict(self.meal, self.alternatives, kcal_fraction = self.kcal_fraction, maintenance = self.maintenance)


    def run(self, maintenance, categories, kcal_fraction, week, day_of_week, time):
        """
        Takes input for a single meal at time <time> on day <day_of_week> in week <week>,
        runs the methods get_category_meals, get_random_meal and add_meal_to_meal_plan.
        """
        self.maintenance = maintenance
        self.categories = tuple(sorted(categories))
        self.kcal_fraction = float(kcal_fraction) / 100
        self.week = week
        self.day_of_week = day_of_week
        self.time = time
        self.get_category_meals()
        self.get_random_meal()

        if week not in self.meal_plan:
            self.meal_plan[week] = {}

        if day_of_week not in self.meal_plan[week]:
            self.meal_plan[week][day_of_week] = {}
        
        self.add_meal_to_meal_plan()


def weight_change_to_original_weight(w, wt):
    w = float(w)
    if wt == "st":
        w_lbs = w * 2.205
        w = str(round(w_lbs // 14))
        wa = str(round(w_lbs % 14, 1))
        return "{}st {} {}".format(w, wa, "lbs")

    elif wt == "lbs":
        w = str(round(w*2.205, 1))
        return "{} lbs".format(w)

    else:
        return "{} kg".format(str(round(w, 1)))


import time as timeScript

def create_meal_plan(request, form, meal_plan_obj=False):
    """
    Takes cleaned data from meal_plan_form and creates the meal plan.
    First it creates the MealplanObject and then in a for loop it starts 
    appending days to the meal plan dictionary in the MealPlanObject
    according to the selected meal plan template.
    """
    time_now = timeScript.time()

    name = form.cleaned_data['name']
    client_account = form.cleaned_data['client_account']
    duration = form.cleaned_data['duration']
    mpt = form.cleaned_data['mpt']
    mpt_name = form.cleaned_data['mpt_name']
    adjust = form.cleaned_data['adjust_maintenance']
    
    duration = int(duration)
    client_account = ClientAccount.objects.get( owner = request.user, pk = client_account )
    maintenance = float(client_account.maintenance)
    old_maintenance = float(maintenance)
    age = float(client_account.age)
    w = str(client_account.weight_str)
    w_kg = float(client_account.weight_kg)
    wt = str(client_account.weight_type)
    h_cm = float(client_account.height_cm)
    gender = str(client_account.gender)
    activity_level = float(client_account.activity_level)

    # Big query
    mpt_days = list(DayMealPlanTemplate.objects.filter(owner = request.user, mealplantemplate__pk = mpt ).order_by('day_no').prefetch_related(
        Prefetch(
            'mealmealplantemplate_set',
            queryset = MealMealPlanTemplate.objects.filter(owner = request.user).prefetch_related(
                Prefetch(
                    'meal_categories',
                    queryset = MealCategory.objects.filter(owner = request.user).only('name').all(),
                    to_attr = 'meal_cats'
                    )
            ).order_by('meal_no').all(),
            to_attr = 'mpt_meals'
        )
    ).all())
    no_of_mpt_days = len(mpt_days)
    mp = MealplanObject(request)
    duration *= 7
    total_change = 0
    personal_data = {'weight':[w], 'maintenance':[maintenance]}

    for day in range(duration): 
        day_of_week = day % 7
        
        mpt_day = day % no_of_mpt_days
        mpt_day = mpt_days[mpt_day]

        day_fraction = float(mpt_day.maintenance_fraction) / 100

        total_change += day_fraction
        if day_of_week == 0:
            week = day // 7

        if day_of_week == 6:
            dweight = (total_change - 7) * old_maintenance / 7000
            w_kg = float(w_kg) + dweight
            old_maintenance = calculate_bmr(gender, w_kg, h_cm, age) * activity_level
            personal_data['weight'].append(weight_change_to_original_weight(w_kg, wt))
            personal_data['maintenance'].append(int(round(old_maintenance)))

            if adjust:
                maintenance = float(old_maintenance)
            
            total_change = 0

        for mpt_meal in mpt_day.mpt_meals:
            kcal_fraction = mpt_meal.amount * day_fraction
            categories = [_.name for _ in mpt_meal.meal_cats]
            time = HOUR_VALUES[str(mpt_meal.hour)] + str(mpt_meal.minutes)
            mp.run(maintenance, categories, kcal_fraction, week, day_of_week, time)        

    if meal_plan_obj:
        meal_plan_obj.meal_plan = json.dumps(mp.meal_plan)
        meal_plan_obj.save()
        return meal_plan_obj.meal_plan

    else:
        meal_plan = MealPlan(owner = request.user, client_account = client_account, 
                                    duration = duration, name = name, 
                                    meal_plan = json.dumps(mp.meal_plan),
                                    personal_data = json.dumps(personal_data),
                                    start_weight = personal_data['weight'][0],
                                    end_weight = personal_data['weight'][-1],
                                    start_maintenance = personal_data['maintenance'][0],
                                    end_maintenance = personal_data['maintenance'][-1],
                                    template = mpt_name,
                                    form = json.dumps(form.cleaned_data))

        meal_plan.save()
        dtime = timeScript.time() - time_now
        print("IT TOOK: " + str(dtime) + "s")
        return meal_plan

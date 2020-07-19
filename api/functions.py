
from ingredients.models import *
from mealplans.models import *
from meals.models import *
from clientaccounts.models import *


def get_model_object(category):
    if category == 'meals':
        object_cat = Meal
    elif category == 'ingredients':
        object_cat = Ingredient
    elif category == 'clientaccounts':
        object_cat = ClientAccount
    elif category == 'meals-categories':
        object_cat = MealCategory
    elif category == 'ingredients-tags':
        object_cat = IngredientTag
    elif category == 'mealplans-templates':
        object_cat = MealPlanTemplate
    elif category == 'mealplans':
        object_cat = MealPlan
    else:
        object_cat = None
    return object_cat

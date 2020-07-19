import itertools

from django.db.models import Q

from .models import *

from ingredients.models import Ingredient, IngredientTag
from ws.forms import FormCleanedData

from ws.functions import calculate_kcal, list_2_unordered_list
from ws.static_variables import WEIGHT_MULTIPLIERS


class Meal_object:
    def __init__(self, comment, add_ing_comment):
        self.protein = 0
        self.carbs = 0
        self.sugars = 0
        self.fibers = 0
        self.fats = 0
        self.saturated_fats = 0
        self.unsaturated_fats = 0
        self.salt = 0
        self.name = []

        self.comment = comment
        self.ing_comment = []
        self.add_ing_comment = add_ing_comment
        self.final_dict = {}

    def add_ingredient_to_meal(self,ingr,multiplier):
        self.protein += float(ingr.protein)*multiplier
        self.carbs += float(ingr.carbs)*multiplier
        self.sugars += float(ingr.sugars)*multiplier
        self.fibers += float(ingr.fibers)*multiplier
        self.fats += float(ingr.fats)*multiplier
        self.saturated_fats += float(ingr.saturated_fats)*multiplier
        self.unsaturated_fats += float(ingr.unsaturated_fats)*multiplier
        self.salt += float(ingr.salt)*multiplier
        self.name.append(ingr.name)
        
        if self.add_ing_comment:
            self.ing_comment.append(ingr.comments)

        ingr.used = int(ingr.used) + 1 
        ingr.save()

    def final_calculation(self, custom_cats, name = False):
        self.final_dict['kcals'] = calculate_kcal(self.protein, self.carbs, self.fats)
        self.final_dict['leanness'] = round(100 * self.protein * 4 / self.final_dict['kcals'], 1)
        self.final_dict['protein'] = self.protein
        self.final_dict['carbs'] = self.carbs
        self.final_dict['categories'] = ', '.join(custom_cats)
        self.final_dict['sugars'] = self.sugars
        self.final_dict['fibers'] = self.fibers
        self.final_dict['fats'] = self.fats
        self.final_dict['saturated_fats'] = self.saturated_fats
        self.final_dict['unsaturated_fats'] = self.unsaturated_fats
        self.final_dict['salt'] = self.salt
        self.final_dict['energy'] = self.final_dict['kcals']*4.18

        if 'temp_name' in name:
            if len(self.name) > 1:
                self.final_dict['name'] = ', '.join(self.name[:-1]) + ' & ' + self.name[-1]
            else:
                self.final_dict['name'] = self.name[0]
            
        else:
            self.final_dict['name'] = name
        
        self.ing_comment += [self.comment]
        self.ing_comment = [_ for _ in self.ing_comment if _ != 'NULL']
        self.final_dict['comment'] = "\n".join(self.ing_comment).strip(' ').strip('\n').strip(' ')
        self.final_dict['add_ing_comment'] = self.add_ing_comment


def add_category_to_meal(request, meal = None, category = None):
    """
    Takes meal oject and category and adds category to many-to-many 
    category field of meal. Returns meal and custom categories list.
    """

    category = [''.join([__ for __ in _ if (__.isalnum() or __==' ')]).strip(' ') for _ in category.replace('"','').lower().split('value:')]
    custom_cats = list(sorted([_ for _ in list(set(category)) if (_.replace(' ','') != '')]))
    set_custom_cats = set(custom_cats)

    old_meal_cats = [_.name for _ in list(meal.category.only('name').all())]
    set_old_meal_cats = set(old_meal_cats)
    remove_cats = list(set_old_meal_cats - set_custom_cats)
    add_new_cats = list(set_custom_cats - set_old_meal_cats)

    for cat in remove_cats:
        cat_object = MealCategory.objects.filter(owner = request.user).get(name = cat)
        meal.category.remove(cat_object)

    for cat in add_new_cats:
        try:
            cat_object = MealCategory.objects.filter(owner = request.user).get(name = cat)
        except MealCategory.DoesNotExist:
            cat_object = MealCategory()
            cat_object.owner = request.user
            cat_object.name = cat
            cat_object.save()

        meal.category.add(cat_object)
        
    return meal, custom_cats


def meal_data(request = None, name = 'temp_name', category =  None, meal = False, meal_ingredient_formset = None, comment = '', add_ing_comment = False):
    """
    Gets and cleans meal data and creates meal object. 
    Adds relationship to meal category, 
    creates the category if it doesn't exist.
    Creates meal ingredient objects.
    Returns meal
    """

    if not meal:
        meal = Meal(owner = request.user, name = name)
        meal.save()

    # Add category to meal
    meal, custom_cats = add_category_to_meal(request, meal = meal, category = category)
    
    # Get ingredients and delete them if they exist
    meal_ingredients = MealIngredient.objects.filter(meal = meal, owner = request.user)
    meal_ingredients.delete()

    # Create new instance of meal_object 
    temp_meal = Meal_object(comment, add_ing_comment)
    for meal_ingredient_form in meal_ingredient_formset:
        original_quantity = meal_ingredient_form.cleaned_data['original_quantity']
        amount_type = meal_ingredient_form.cleaned_data['amount_type']
        ingredient = meal_ingredient_form.cleaned_data['ingredient']

        if type(ingredient) == str:
            ingredient = Ingredient.objects.get( pk = ingredient )

        multiplier = WEIGHT_MULTIPLIERS[amount_type]*float(original_quantity)

        temp_meal.add_ingredient_to_meal(ingredient, multiplier)
        MealIngredient.objects.create(owner = request.user, meal=meal, quantity=multiplier, ingredient=ingredient, original_quantity=original_quantity, amount_type=amount_type)

    temp_meal.final_calculation(custom_cats, name=name)

    for k,v in temp_meal.final_dict.items():
        setattr(meal, k, v)

    meal.save()
    return meal


def get_ingredients_with_tags(request, cleaned_tags, ingredients, total_ingredients, cleaned_quantity=False, amount_type=False):
    """
    Creates list of ingredients list with unique ingredients per given number of tags.
    Returns list of list of ingredients (in the case that cleaned_quantity != False, returns list of lists of ingredient objects)
    """
    tag_filter = Q()
    for tagid in cleaned_tags:
        tag_filter |= Q(pk = tagid, owner = request.user)
    
    found_tags = IngredientTag.objects.filter(tag_filter)
    if len(found_tags) > 0:
        new_ingredients = Ingredient.objects.filter(owner = request.user, tag = found_tags[0])
        if len(found_tags) > 1:
            for tag in found_tags[1:]:
                new_ingredients = new_ingredients.filter(tag = tag)
        
        new_ingredients = list(new_ingredients)
        if cleaned_quantity:
            new_ingredients = [FormCleanedData({'original_quantity':cleaned_quantity, 'ingredient':ing, 'amount_type': amount_type}) for ing in new_ingredients if ing not in total_ingredients]
            total_ingredients += [_.cleaned_data['ingredient'] for _ in new_ingredients]
        else:
            new_ingredients = [ing.id for ing in new_ingredients if ing.id not in total_ingredients]
            total_ingredients += [_ for _ in new_ingredients]

        ingredients.append(new_ingredients)
        
    else:
        ingredients.append([])
    
    return ingredients, total_ingredients


def tag_meal_data(request, category = None, tag_meal_ingredient_formset = None, comment=None, add_ing_comment=None):
    """
    Creates meals from the selected ingredient tags. Calls the meal_data method.
    Returns a list of created meals. 
    """
    ingredients = []
    total_ingredients = []
    for form in tag_meal_ingredient_formset:
        cleaned_tags = [_.strip(' ').lower() for _ in form.cleaned_data['tag'].split(';:') if _.replace(' ','') != '']
        cleaned_quantity = form.cleaned_data['original_quantity']
        amount_type = form.cleaned_data['amount_type']
        ingredients, total_ingredients = get_ingredients_with_tags(request, cleaned_tags, ingredients, total_ingredients, cleaned_quantity=cleaned_quantity, amount_type=amount_type)
    
    meals = itertools.product(*ingredients)
    meals_list = []
    for meal in meals:
        meals_list.append(meal_data(request = request, category = category, meal_ingredient_formset = meal, comment=comment, add_ing_comment=add_ing_comment))
    
    return meals_list
from functools import reduce

from django.dispatch import receiver
from django.db.models.signals import post_save, m2m_changed
from django.db.models import Value, F
from django.contrib.postgres.search import SearchVector
from django.db import transaction

from clientaccounts.models import ClientAccount
from ingredients.models import Ingredient, IngredientTag
from mealplans.models import MealPlan, MealPlanTemplate

import operator

@receiver(post_save)
def on_save(sender, **kwargs):
    if not issubclass(sender, (MealPlan, MealPlanTemplate, ClientAccount, Ingredient, IngredientTag)):
        return
    transaction.on_commit(make_updater(kwargs['instance']))


@receiver(m2m_changed)
def on_m2m_changed(sender, **kwargs):
    instance = kwargs['instance']
    model = kwargs['model']
    if model is Ingredient or model is IngredientTag:
        transaction.on_commit(make_updater(instance))
    elif isinstance(instance, (MealPlan, MealPlanTemplate, ClientAccount, Ingredient, IngredientTag)):
        for obj in model.objects.filter(pk__in=kwargs['pk_set']):
            transaction.on_commit(make_updater(obj))


def make_updater(instance):
    pk = instance.pk
    def on_commit():
        instance.__class__.objects.filter(pk=pk).update(
            search_name=SearchVector('name'))
    return on_commit
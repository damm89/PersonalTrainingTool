from django.db import models
from django.conf import settings

from ingredients.models import Ingredient
from ws.models import SearchableModel, OwnerModel
from ws.functions import model_unique_name

class MealCategory(SearchableModel):
    used = models.SmallIntegerField(default=0)

class Meal(SearchableModel):
    carbs = models.DecimalField(max_digits=10, decimal_places=1, default=0)
    category = models.ManyToManyField(MealCategory)
    categories = models.CharField(max_length=510, default="")
    energy = models.DecimalField(max_digits=10, decimal_places=1, default=0)
    fats = models.DecimalField(max_digits=10, decimal_places=1, default=0)
    fibers = models.DecimalField(max_digits=10, decimal_places=1, default=0)
    kcals = models.DecimalField(max_digits=10, decimal_places=1, default=0)
    leanness = models.DecimalField(max_digits=10, decimal_places=1, default=0)
    protein = models.DecimalField(max_digits=10, decimal_places=1, default=0)
    salt = models.DecimalField(max_digits=10, decimal_places=1, default=0)
    saturated_fats = models.DecimalField(max_digits=10, decimal_places=1, default=0)
    sugars = models.DecimalField(max_digits=10, decimal_places=1, default=0)
    unsaturated_fats = models.DecimalField(max_digits=10, decimal_places=1, default=0)

    # Added 2020-01-13
    comment = models.TextField(default="")
    add_ing_comment = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        self.name = model_unique_name(self, Meal, self.name)
        super().save(*args, **kwargs)


class MealIngredient(OwnerModel):
    meal = models.ForeignKey(Meal, on_delete=models.CASCADE)
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE)
    original_quantity = models.DecimalField(max_digits=10, decimal_places=1, default=0)
    amount_type = models.CharField(max_length=10, default='')
    quantity = models.DecimalField(max_digits=14, decimal_places=4, default=0)
from django.db import models
from django.conf import settings

from meals.models import MealCategory
from clientaccounts.models import ClientAccount
from ws.models import SearchableModel, OwnerModel
from ws.functions import model_unique_name

# Create your models here.
class MealPlanTemplate(SearchableModel):    
    name = models.CharField(max_length=255, default="", unique=True)
    template = models.TextField(default="")

    # Added 2020-01-15
    status = models.CharField(max_length=23, default='Not working')
    is_working = models.BooleanField(default=False)

    def create_mpt_days(self, data):
        for day in data:
            maintenance_fraction = data[day].pop('maintenance_fraction')
            mpt_day = DayMealPlanTemplate(owner = self.owner, mealplantemplate = self, day_no = day.split('d')[-1], maintenance_fraction = maintenance_fraction)
            mpt_day.save(day_data=data[day], owner=self.owner)

    def save(self, *args, **kwargs):
        data = kwargs.pop('data')
        self.name = model_unique_name(self, MealPlanTemplate, self.name)
        super().save(*args, **kwargs)
        self.create_mpt_days(data)


class DayMealPlanTemplate(OwnerModel):
    mealplantemplate = models.ForeignKey(MealPlanTemplate, on_delete=models.CASCADE)
    day_no = models.PositiveSmallIntegerField(default = 0)
    maintenance_fraction = models.PositiveSmallIntegerField(default = 0)

    def create_mpt_meal(self, day_data, owner):
        for meal in day_data:
            hour = day_data[meal]['hour']
            minutes = day_data[meal]['minutes']
            meal_no = meal.split('m')[-1]
            amount = day_data[meal]['amount']
            categories = [MealCategory.objects.filter(owner = owner).get(pk = mcid) for mcid in day_data[meal]['mealCats'].split(';:')]
            mpt_meal = MealMealPlanTemplate.objects.create(owner = owner, day = self, meal_no = meal_no, hour = hour, minutes = minutes, amount = amount)
            for cat in categories:
                mpt_meal.meal_categories.add(cat)

            mpt_meal.save()

    def save(self, *args, **kwargs):
        day_data = kwargs.pop('day_data')
        owner = kwargs.pop('owner')
        super().save(*args, **kwargs)
        self.create_mpt_meal(day_data, owner)


class MealMealPlanTemplate(OwnerModel):
    day = models.ForeignKey(DayMealPlanTemplate, on_delete=models.CASCADE)
    amount = models.PositiveIntegerField(default = 0)
    meal_no = models.PositiveIntegerField(default = 0)
    hour = models.CharField(max_length = 4, default = '')
    minutes = models.CharField(max_length = 2, default = '')
    meal_categories = models.ManyToManyField(MealCategory)


class MealPlan(SearchableModel):
    client_account = models.ForeignKey(ClientAccount, on_delete=models.CASCADE)
    duration = models.PositiveSmallIntegerField(default=0)
    meal_plan = models.TextField(default='')
    personal_data = models.TextField(default='')
    template = models.CharField(max_length=255, default='')

    # Added 2020-01-15
    start_weight = models.CharField(max_length=15, default='')
    end_weight = models.CharField(max_length=15, default='')
    start_maintenance = models.CharField(max_length=15, default='')
    end_maintenance = models.CharField(max_length=15, default='')

    # Added 2020-02-21
    form = models.TextField(default='')

    def save(self, *args, **kwargs):
        self.name = model_unique_name(self, MealPlan, self.name)
        super().save(*args, **kwargs)

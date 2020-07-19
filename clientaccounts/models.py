from django.db import models
from django.conf import settings
from django.contrib.postgres.search import SearchVectorField
from django.contrib.postgres.indexes import GinIndex

from .static_variables import ACTIVITY_LEVEL_CHOICES, GENDER_CHOICES, ACTIVITY_LEVEL_DICT

from ws.models import SearchableModel
from ws.static_variables import WEIGHT_MULTIPLIERS
from ws.functions import str2fl, calculate_bmr, model_unique_name


class ClientAccount(SearchableModel):
    activity_level = models.CharField(max_length=5, choices=ACTIVITY_LEVEL_CHOICES, default="NULL")
    activity_level_readable = models.CharField(max_length=43, default="NULL")
    age = models.PositiveSmallIntegerField(default=0)
    bmr = models.PositiveSmallIntegerField(default=0)
    comments = models.TextField(default="NULL", max_length=1000)
    gender = models.CharField(max_length=6, choices=GENDER_CHOICES, default="NULL")
    height = models.PositiveSmallIntegerField(default=0)
    maintenance = models.PositiveSmallIntegerField(default=0)
    
    weight = models.DecimalField(max_digits=5,decimal_places=1, default=0)

    # Added 2020-01-15
    email = models.CharField(default='NULL', max_length=100)

    # Added 2020-01-19
    height_type = models.CharField(max_length=10, default='')
    weight_type = models.CharField(max_length=10, default='')
    height_add = models.PositiveSmallIntegerField(default=0)
    weight_add = models.DecimalField(max_digits=3, decimal_places=1, default=0)
    height_str = models.CharField(max_length=20, default='')
    weight_str = models.CharField(max_length=20, default='')
    height_cm = models.DecimalField(max_digits=4, decimal_places=1, default=0)
    weight_kg = models.DecimalField(max_digits=4, decimal_places=1, default=0)

    def set_weight_str(self):
        """
        Sets weight string to be shown in table
        """
        if self.weight_type == 'st':
            weight_str = str(round(self.weight), 1)
            self.weight_str = "{}st {} lbs".format(self.weight_str, str(round(self.weight_add, 1)) )
        else:
            weight_str = str(round(self.weight,1))
            self.weight_str = "{} {}".format(weight_str, self.weight_type)


    def set_weight_kg(self):
        """
        Normalizes weight to kg
        """
        self.weight = str2fl(self.weight)

        if self.weight_type == 'st':
            self.weight_add = str2fl(self.weight_add)
            self.weight_kg = ( self.weight * 14 + self.weight_add ) / 2.205
        elif self.weight_type == 'lbs':
            self.weight_kg = self.weight / 2.205
        else:
            self.weight_kg = float(self.weight)


    def set_height_cm(self):
        """
        Normalizes height to cm
        """
        self.weight_add = str2fl(self.weight_add)
        self.weight = str2fl(self.weight)

        if self.height_type == 'ft':
            self.height_cm = (self.height * 12 + self.height_add) * 2.54
        else:
            self.height_cm = float(self.height)

    def set_height_str(self):
        """
        Sets height string to be shown in table
        """

        self.height_add = str2fl(self.height_add)
        self.height = str2fl(self.height)

        if self.height_type == 'ft':
            self.height_str = "{}ft {} in".format(round(self.height,0), round(self.height_add,1))
        else:
            self.height_str = "{}{}".format(round(self.height,0),self.height_type)
    
    def calculate_maintenance(self):
        """
        Takes BMR and multiplies it with activity level multiplier
        """
        self.activity_level = str2fl(self.activity_level)
        self.maintenance = round(self.bmr * self.activity_level)

    def account_data(self):
        """
        Sets all the normalized account data such as
        height in cm, 
        weight in kg,
        etc.
        Calls self.set_weight_kg, self.set_weight_str, 
        self.set_height_cm, self.set_height_str, str2fl,
        calculate_bmr, self.calculate_maintenance.
        """
        self.activity_level_readable = ACTIVITY_LEVEL_DICT[self.activity_level]
        self.name = self.name.capitalize()

        self.set_weight_kg()
        self.set_weight_str()

        self.set_height_cm()
        self.set_height_str()

        self.age = str2fl(self.age)
        self.bmr = calculate_bmr(self.gender, self.weight_kg, self.height_cm, self.age)

        self.calculate_maintenance()
    
    def save(self, *args, **kwargs):
        self.account_data()
        self.name = model_unique_name(self, ClientAccount, self.name)
        super().save(*args,**kwargs)

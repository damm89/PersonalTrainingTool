from django.db import models
from django.conf import settings

from django.contrib.postgres.search import SearchVector

from ws.models import SearchableModel
from ws.static_variables import WEIGHT_MULTIPLIERS
from ws.functions import calculate_kcal, list_2_unordered_list, model_unique_name



class IngredientTag(SearchableModel):
    # Added 2019-12-24
    used = models.SmallIntegerField(default=0)

class Ingredient(SearchableModel):    
    amount = models.DecimalField(max_digits=14, decimal_places=1, default=0)
    amount_type = models.CharField(max_length=10, default='')
    carbs = models.DecimalField(max_digits=10, decimal_places=1, default=0)
    energy = models.DecimalField(max_digits=10, decimal_places=1, default=0)
    fats = models.DecimalField(max_digits=10, decimal_places=1, default=0)
    fibers = models.DecimalField(max_digits=10, decimal_places=1, default=0)
    kcals = models.DecimalField(max_digits=10, decimal_places=1, default=0)
    protein = models.DecimalField(max_digits=10, decimal_places=1, default=0)
    salt = models.DecimalField(max_digits=10, decimal_places=1, default=0)
    saturated_fats = models.DecimalField(max_digits=10, decimal_places=1, default=0)
    sugars = models.DecimalField(max_digits=10, decimal_places=1, default=0)
    unsaturated_fats = models.DecimalField(max_digits=10, decimal_places=1, default=0)

    original_carbs = models.DecimalField(max_digits=10, decimal_places=1, default=0)
    original_energy = models.DecimalField(max_digits=10, decimal_places=1, default=0)
    original_fats = models.DecimalField(max_digits=10, decimal_places=1, default=0)
    original_fibers = models.DecimalField(max_digits=10, decimal_places=1, default=0)
    original_kcals = models.DecimalField(max_digits=10, decimal_places=1, default=0)
    original_protein = models.DecimalField(max_digits=10, decimal_places=1, default=0)
    original_salt = models.DecimalField(max_digits=10, decimal_places=1, default=0)
    original_saturated_fats = models.DecimalField(max_digits=10, decimal_places=1, default=0)
    original_sugars = models.DecimalField(max_digits=10, decimal_places=1, default=0)
    original_unsaturated_fats = models.DecimalField(max_digits=10, decimal_places=1, default=0)
    comments = models.TextField(default="", max_length=500)  

    # Added 2019-11-19
    used = models.PositiveSmallIntegerField(default=1)

    # Added 2019-11-28
    tag = models.ManyToManyField(IngredientTag)
    tags = models.CharField(max_length=510, default="")

    # Added 2020-01-17
    amount_list = models.CharField(max_length=20, default='')

    def add_standard_amount(self):
        """
        Adds a standard amount of the ingredient macro's of the ingredient to the ingredient. 
        Macro's are all counted per 100 grams or pieces not per X ounce or Y pounds or whatever.
        """
        self.amount = str(self.amount)
        self.amount = '.'.join([''.join([__ for __ in _ if __.isnumeric()]) for _ in self.amount.replace(',','.').split('.')])
        self.amount_type = ''.join([_ for _ in self.amount_type if (_.isalpha() and _ != ' ')])
        if self.amount_type == 'gram':
            amount_str = 'g'
        else:
            amount_str = ' ' + self.amount_type

        self.amount_list = self.amount + amount_str

        if self.amount_type in WEIGHT_MULTIPLIERS:
            multiplier = WEIGHT_MULTIPLIERS[self.amount_type] * float(self.amount)
        else:
            self.amount_type = 'piece'
            self.amount = 1
            multiplier = 1

        self.name = self.name.capitalize()
        self.protein = round(float(self.original_protein) / multiplier, 1)
        self.carbs = round(float(self.original_carbs) / multiplier, 1)
        self.sugars = round(float(self.original_sugars) / multiplier, 1)
        self.fibers = round(float(self.original_fibers) / multiplier, 1)
        self.fats = round(float(self.original_fats) / multiplier, 1)
        self.saturated_fats = round(float(self.original_saturated_fats) / multiplier, 1)
        self.unsaturated_fats = round(float(self.original_unsaturated_fats) / multiplier, 1)
        self.salt = round(float(self.original_salt) / multiplier, 1)
        self.kcals = calculate_kcal(self.protein, self.carbs, self.fats)
        self.energy = round(self.kcals * 4.18, 1)

    def add_tags(self, tag_form):
        """
        Adds, creates/edits and removes IngredientTag when self.save(tag_form = tag_form) is called.
        """
        if type(tag_form) != str:
            tags = tag_form.cleaned_data.get('tag','')
            tags = [''.join([__ for __ in _ if (__.isalnum() or __==' ')]) for _ in tags.replace('"','').lower().split('value:')]

        else:
            tags = [''.join([__ for __ in _ if (__.isalnum() or __==' ')]) for _ in tag_form.replace('"','').lower().split(',')]
        
        tags = list(sorted([_.strip(' ').lower() for _ in list(set(tags)) if (_.replace(' ','')!='')]))
        new_tags = []
        for tag in tags:
            try:
                tag_object = IngredientTag.objects.get(owner = self.owner, name = tag)
                new_tags.append(tag_object)

            except IngredientTag.DoesNotExist:
                try:
                    tag_object = IngredientTag.objects.create(owner = self.owner, name = tag)
                    new_tags.append(tag_object)

                except Exception:
                    print("{} wasn't created.".format(tag_object.name))

        old_tags = list(self.tag.all())
        for tag in old_tags:
            if tag not in new_tags:
                self.tag.remove(tag)
                tag.used -= 1
                tag.save()

        tags = []
        for tag in new_tags:
            try:
                if tag not in old_tags:
                    self.tag.add(tag)
                    tag.used += 1
                    tag.save()
                tags.append(tag.name)

            except Exception:
                print("{} wasn't added.".format(tag.name))
        
        self.tags = ", ".join(tags)
    
    def remove_tag(self, tag, *args, **kwargs):
        """
        Removes tag object from m2m relationship and updates the tags field.
        Calls super().save afterwards.
        """
        self.tag.remove(tag)
        tags = self.tags.lower().split(', ')
        tags.remove(tag.name.lower())
        self.tags = ', '.join(tags)
        super().save(*args, **kwargs)


    def save(self, *args, **kwargs):
        """
        Calls:
            1) self.add_standard_amount to normalize data
            2) model_unique_name to make sure ingredient has a unique name 
            3) super().save(*args, **kwargs) to initalize ingredient
            4) self.add_tags to add and/or remove ingredienttags from the ingredient
            5) super().save(*args, update_fields=['tags'], **kwargs) to update tags field
        """
        
        self.add_standard_amount()
        self.name = model_unique_name(self, Ingredient, self.name)
        if 'tag_form' in kwargs:
            tag_form = kwargs.pop('tag_form')
        else:
            tag_form = False

        super().save(*args, **kwargs)
        
        if tag_form:
            self.add_tags(tag_form)
            kwargs['update_fields'] = ['tags']
            super().save(*args, **kwargs)
